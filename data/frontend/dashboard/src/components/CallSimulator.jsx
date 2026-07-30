import { motion, AnimatePresence } from 'framer-motion'
import { useState, useRef, useEffect } from 'react'
import { Phone, PhoneOff, Send, Bot, User, Loader2, Volume2, VolumeX, PhoneCall } from 'lucide-react'
import api from '../api'

export default function CallSimulator({ clientData }) {
  const [callActive, setCallActive] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [leadId, setLeadId] = useState('')
  const [leadSearch, setLeadSearch] = useState('')
  const [leads, setLeads] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [product, setProduct] = useState('AI-powered CRM software that helps businesses grow')
  const [voiceOn, setVoiceOn] = useState(true)
  const [voiceCallStatus, setVoiceCallStatus] = useState(null) // null, ringing, connected, completed
  const [voiceCallId, setVoiceCallId] = useState(null)
  const chatRef = useRef(null)
  const inputRef = useRef(null)

  const speakText = (text) => {
    if (!voiceOn) return
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1.0
      utterance.pitch = 1.0
      utterance.lang = 'en-US'
      const voices = window.speechSynthesis.getVoices()
      const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Samantha'))
      if (femaleVoice) utterance.voice = femaleVoice
      window.speechSynthesis.speak(utterance)
    }
  }

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [messages, loading])

  useEffect(() => {
    api.get('/leads').then(res => setLeads(res.data.leads || [])).catch(() => {})
  }, [])

  const filteredLeads = leads.filter(l =>
    l.name?.toLowerCase().includes(leadSearch.toLowerCase()) ||
    l.phone?.includes(leadSearch)
  )

  const selectLead = (lead) => {
    setLeadId(lead.id)
    setLeadSearch(`${lead.name} (${lead.phone})`)
    setShowSuggestions(false)
  }

  const startCall = async () => {
    if (!leadId) return
    setLoading(true)
    try {
      const res = await api.post('/call/start', { lead_id: parseInt(leadId) })
      setConversationId(res.data.conversation_id)
      setCallActive(true)
      setMessages([{ role: 'ai', content: res.data.ai_message }])
      speakText(res.data.ai_message)
      setAnalysis(null)
    } catch (err) {
      setMessages([{ role: 'system', content: 'Error: Lead not found. Add a lead first!' }])
    }
    setLoading(false)
  }

  const sendMessage = async () => {
    if (!input.trim() || !conversationId) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'human', content: userMsg }])
    setLoading(true)
    try {
      const res = await api.post(`/call/respond?conversation_id=${conversationId}`, { message: userMsg })
      setMessages(prev => [...prev, { role: 'ai', content: res.data.ai_message }])
      speakText(res.data.ai_message)

      // Auto-end call if lead or AI says bye
      const endWords = ['bye', 'goodbye', 'good bye', 'talk later', 'thanks bye', 'ok bye', 'okay bye', 'have a great day', 'have a good day', 'take care']
      const lastMsg = res.data.ai_message.toLowerCase()
      const userLower = userMsg.toLowerCase()
      if (endWords.some(w => userLower.includes(w)) || endWords.some(w => lastMsg.includes(w))) {
        setLoading(false)
        setTimeout(() => endCall(), 1000)
        return
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'system', content: 'Error getting AI response' }])
    }
    setLoading(false)
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  const endCall = async () => {
    if (!conversationId) return
    setLoading(true)
    try {
      const res = await api.post(`/call/end?conversation_id=${conversationId}`, {})
      setAnalysis(res.data)
    } catch (err) {}
    setCallActive(false)
    setConversationId(null)
    setLoading(false)
  }

  // Real Voice Call
  const startVoiceCall = async () => {
    if (!leadId) return
    setLoading(true)
    try {
      const res = await api.post('/voice/call', { lead_id: parseInt(leadId) })
      setVoiceCallId(res.data.call_id)
      setVoiceCallStatus('ringing')
      setMessages([{ role: 'system', content: '📞 Dialing... Real AI voice call initiated!' }])
      // Poll status
      const poll = setInterval(async () => {
        try {
          const s = await api.get(`/voice/status/${res.data.call_id}`)
          setVoiceCallStatus(s.data.status)
          if (s.data.status === 'completed') clearInterval(poll)
        } catch { clearInterval(poll) }
      }, 3000)
    } catch (err) {
      setMessages([{ role: 'system', content: `❌ ${err.response?.data?.detail || 'Voice call failed. Check Twilio config.'}` }])
    }
    setLoading(false)
  }

  const endVoiceCall = async () => {
    if (!voiceCallId) return
    setLoading(true)
    try {
      const res = await api.post(`/voice/end?call_id=${voiceCallId}`)
      setAnalysis(res.data.analysis ? { analysis: res.data.analysis } : null)
      setMessages(prev => [...prev, { role: 'system', content: '📞 Voice call ended.' }])
    } catch (err) {}
    setVoiceCallStatus(null)
    setVoiceCallId(null)
    setLoading(false)
  }

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ marginBottom: '20px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)' }}>Call Simulator</h1>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Test AI conversations without real calls</p>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '12px' }}>
        {/* Left Panel - Call Setup */}
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', overflow: 'auto' }}>
          <p style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '16px' }}>Call Setup</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '16px' }}>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Select Lead</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="Type name or phone..."
                  value={leadSearch}
                  onChange={e => { setLeadSearch(e.target.value); setShowSuggestions(true); setLeadId('') }}
                  onFocus={() => setShowSuggestions(true)}
                  className="input"
                  disabled={callActive}
                />
                {showSuggestions && leadSearch && filteredLeads.length > 0 && !callActive && (
                  <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '4px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '9px', maxHeight: '160px', overflowY: 'auto', zIndex: 10 }}>
                    {filteredLeads.map(lead => (
                      <div
                        key={lead.id}
                        onClick={() => selectLead(lead)}
                        style={{ padding: '10px 14px', cursor: 'pointer', borderBottom: '1px solid var(--border)', fontSize: '12px', transition: 'all 0.15s' }}
                        onMouseEnter={e => e.currentTarget.style.background = 'var(--accent-bg)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                      >
                        <p style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{lead.name}</p>
                        <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>{lead.phone}</p>
                      </div>
                    ))}
                  </div>
                )}
                {showSuggestions && leadSearch && filteredLeads.length === 0 && (
                  <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '4px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '9px', padding: '12px', fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center' }}>
                    No leads found. Add one from Leads page.
                  </div>
                )}
              </div>
            </div>
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Product Info</label>
              <textarea placeholder="What should AI pitch?" value={product} onChange={e => setProduct(e.target.value)} className="input" style={{ height: '80px', resize: 'none' }} disabled={callActive} />
            </div>
          </div>

          {!callActive && !voiceCallStatus ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button onClick={startCall} disabled={loading || !leadId} className="btn" style={{ width: '100%', justifyContent: 'center', padding: '12px', opacity: (!leadId || loading) ? 0.5 : 1, background: 'linear-gradient(135deg, #10b981, #059669)', color: 'white' }}>
                {loading ? <Loader2 size={15} className="animate-spin" /> : <Phone size={15} />} Simulate Call
              </button>
              <button onClick={startVoiceCall} disabled={loading || !leadId} className="btn" style={{ width: '100%', justifyContent: 'center', padding: '12px', opacity: (!leadId || loading) ? 0.5 : 1, background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)', color: 'white' }}>
                {loading ? <Loader2 size={15} className="animate-spin" /> : <PhoneCall size={15} />} Real Voice Call
              </button>
            </div>
          ) : voiceCallStatus ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.3)', textAlign: 'center' }}>
                <p style={{ fontSize: '11px', color: '#a78bfa', fontWeight: '600' }}>🔊 Voice Call: {voiceCallStatus}</p>
              </div>
              <button onClick={endVoiceCall} className="btn" style={{ width: '100%', justifyContent: 'center', padding: '12px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white' }}>
                <PhoneOff size={15} /> End Voice Call
              </button>
            </div>
          ) : (
            <button onClick={endCall} className="btn" style={{ width: '100%', justifyContent: 'center', padding: '12px', background: 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white' }}>
              <PhoneOff size={15} /> End Call
            </button>
          )}

          {/* Analysis */}
          <AnimatePresence>
            {analysis && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={{ marginTop: '12px', padding: '14px', borderRadius: '10px', background: 'var(--accent-bg)', border: '1px solid var(--accent-border)' }}>
                <p style={{ fontSize: '12px', fontWeight: '600', color: 'var(--accent-light)', marginBottom: '10px' }}>Analysis</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Sentiment</span>
                    <span style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{analysis.analysis?.sentiment}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Score</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: '700' }}>{analysis.analysis?.score}/10</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Category</span>
                    <span className={`badge badge-${analysis.analysis?.category}`}>{analysis.analysis?.category}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Panel - Chat Box FIXED HEIGHT */}
        <div className="card" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          
          {/* Header - Fixed top */}
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div className={callActive ? 'dot-live' : ''} style={!callActive ? { width: '7px', height: '7px', borderRadius: '50%', background: 'var(--text-dim)' } : {}}></div>
              <span style={{ fontSize: '12px', fontWeight: '500', color: callActive ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                {callActive ? 'Call Active' : 'No Active Call'}
              </span>
            </div>
            <button
              onClick={() => { setVoiceOn(!voiceOn); if (voiceOn) window.speechSynthesis.cancel() }}
              style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '7px', padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: voiceOn ? '#06b6d4' : 'var(--text-muted)' }}
            >
              {voiceOn ? <Volume2 size={13} /> : <VolumeX size={13} />}
              {voiceOn ? 'Voice On' : 'Voice Off'}
            </button>
          </div>

          {/* Messages - SCROLLS INSIDE THIS BOX */}
          <div ref={chatRef} style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {messages.length === 0 && (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                  <Phone size={24} style={{ color: 'var(--text-dim)', margin: '0 auto 10px' }} />
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Start a call to begin</p>
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', gap: '8px', justifyContent: msg.role === 'human' ? 'flex-end' : 'flex-start' }}>
                {msg.role === 'ai' && (
                  <div style={{ width: '28px', height: '28px', borderRadius: '7px', background: 'var(--accent-bg)', border: '1px solid var(--accent-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Bot size={13} color="var(--accent-light)" />
                  </div>
                )}
                <div style={{ maxWidth: '70%', padding: '8px 12px', borderRadius: '10px', fontSize: '12px', lineHeight: '1.4', background: msg.role === 'ai' ? 'var(--accent-bg)' : msg.role === 'human' ? 'var(--bg-input)' : 'rgba(239,68,68,0.1)', border: `1px solid ${msg.role === 'ai' ? 'var(--accent-border)' : msg.role === 'human' ? 'var(--border)' : 'rgba(239,68,68,0.2)'}`, color: msg.role === 'system' ? '#f87171' : 'var(--text-primary)' }}>
                  {msg.content}
                </div>
                {msg.role === 'human' && (
                  <div style={{ width: '28px', height: '28px', borderRadius: '7px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <User size={13} color="#34d399" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ width: '28px', height: '28px', borderRadius: '7px', background: 'var(--accent-bg)', border: '1px solid var(--accent-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Bot size={13} color="var(--accent-light)" />
                </div>
                <div style={{ padding: '12px 16px', borderRadius: '12px', background: 'var(--accent-bg)', border: '1px solid var(--accent-border)' }}>
                  <Loader2 size={14} color="var(--accent-light)" className="animate-spin" />
                </div>
              </div>
            )}
          </div>

          {/* Input - FIXED at bottom, never moves */}
          <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', flexShrink: 0, background: 'var(--bg-card)' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input ref={inputRef} type="text" placeholder={callActive ? "Type what the lead says..." : "Start a call first..."} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} disabled={!callActive || loading} className="input" style={{ opacity: callActive ? 1 : 0.4 }} />
              <button onClick={sendMessage} disabled={!callActive || loading || !input.trim()} className="btn btn-primary" style={{ padding: '10px 14px', opacity: (!callActive || !input.trim()) ? 0.4 : 1 }}>
                <Send size={14} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
