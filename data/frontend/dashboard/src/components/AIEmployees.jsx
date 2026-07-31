import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Plus, Bot, Phone, Globe, Mic, X, Play, Pause, Settings, Trash2, Link2 } from 'lucide-react'
import api from '../api'

const VOICES = [
  { id: 'suhani', name: 'Suhani', lang: 'Telugu Female' },
  { id: 'kavitha', name: 'Kavitha', lang: 'Telugu/Hindi Female' },
  { id: 'priya', name: 'Priya', lang: 'Telugu Female' },
  { id: 'shreya', name: 'Shreya', lang: 'English/Hindi Female' },
  { id: 'ritu', name: 'Ritu', lang: 'Hindi Female' },
  { id: 'neha', name: 'Neha', lang: 'Hindi Female' },
  { id: 'aditya', name: 'Aditya', lang: 'Hindi Male' },
  { id: 'rahul', name: 'Rahul', lang: 'Telugu/Hindi Male' },
]

const INDUSTRIES = [
  'Real Estate', 'Education', 'Healthcare', 'Insurance',
  'Finance', 'E-commerce', 'Restaurant', 'Hotel',
  'Recruitment', 'Customer Support', 'Sales', 'Other'
]

export default function AIEmployees() {
  const [employees, setEmployees] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [showScript, setShowScript] = useState(null)
  const [analyzingUrl, setAnalyzingUrl] = useState(false)
  const [urlInput, setUrlInput] = useState('')
  const [form, setForm] = useState({
    name: '',
    role: '',
    industry: '',
    voice: 'suhani',
    languages: 'Telugu, English',
    greeting: '',
    script: '',
    company_name: '',
    company_info: '',
    goals: '',
  })

  useEffect(() => {
    // Load saved employees from localStorage
    const saved = JSON.parse(localStorage.getItem('ai_employees') || '[]')
    setEmployees(saved)
  }, [])

  const saveEmployees = (list) => {
    setEmployees(list)
    localStorage.setItem('ai_employees', JSON.stringify(list))
  }

  const analyzeURL = async () => {
    if (!urlInput.trim()) return
    setAnalyzingUrl(true)
    try {
      const res = await api.post('/ai/analyze-url', { url: urlInput.trim() })
      if (res.data.status === 'success') {
        const d = res.data.data
        setForm({
          ...form,
          company_name: d.company_name || '',
          company_info: d.products || '',
          industry: d.industry || '',
          greeting: d.greeting || '',
          script: d.script || '',
          goals: d.goals || '',
          role: 'AI Sales Executive',
          name: 'Priya',
        })
      }
    } catch (err) {
      alert('Could not analyze URL. Check if the website is accessible.')
    }
    setAnalyzingUrl(false)
  }

  const createEmployee = () => {
    if (!form.name || !form.role || !form.script) return
    const newEmp = {
      id: Date.now(),
      ...form,
      status: 'active',
      total_calls: 0,
      leads_qualified: 0,
      created_at: new Date().toISOString(),
    }
    saveEmployees([...employees, newEmp])
    setForm({ name: '', role: '', industry: '', voice: 'suhani', languages: 'Telugu, English', greeting: '', script: '', company_name: '', company_info: '', goals: '' })
    setShowCreate(false)
  }

  const deleteEmployee = (id) => {
    if (!confirm('Delete this AI Employee?')) return
    saveEmployees(employees.filter(e => e.id !== id))
  }

  const toggleStatus = (id) => {
    saveEmployees(employees.map(e => e.id === id ? { ...e, status: e.status === 'active' ? 'paused' : 'active' } : e))
  }

  return (
    <div>
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)' }}>AI Employees</h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Create and manage your AI voice agents</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn btn-primary"><Plus size={14} /> Create AI Employee</button>
      </motion.div>

      {/* Employee Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '14px' }}>
        {employees.length === 0 ? (
          <div className="card" style={{ padding: '60px', textAlign: 'center', gridColumn: '1 / -1' }}>
            <Bot size={32} style={{ color: 'var(--text-dim)', margin: '0 auto 12px' }} />
            <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>No AI Employees yet</p>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '6px' }}>Create your first AI Employee to start making calls</p>
            <button onClick={() => setShowCreate(true)} className="btn btn-primary" style={{ marginTop: '16px' }}><Plus size={14} /> Create AI Employee</button>
          </div>
        ) : (
          employees.map((emp, i) => (
            <motion.div key={emp.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="card" style={{ padding: '20px' }}>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'linear-gradient(135deg, #06b6d4, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Bot size={20} color="white" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)' }}>{emp.name}</h3>
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{emp.role}</p>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => toggleStatus(emp.id)} style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '6px', padding: '4px 10px', fontSize: '10px', cursor: 'pointer', color: emp.status === 'active' ? '#22c55e' : '#f87171', fontWeight: '600' }}>
                    {emp.status === 'active' ? '● Active' : '● Paused'}
                  </button>
                  <button onClick={() => deleteEmployee(emp.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)' }}><Trash2 size={14} /></button>
                </div>
              </div>

              {/* Details */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <Mic size={12} /> Voice: {VOICES.find(v => v.id === emp.voice)?.name || emp.voice}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <Globe size={12} /> Languages: {emp.languages}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <Phone size={12} /> {emp.total_calls} calls | {emp.leads_qualified} leads
                </div>
              </div>

              {/* Script Preview */}
              <div style={{ padding: '10px', borderRadius: '8px', background: 'var(--bg-input)', border: '1px solid var(--border)', marginBottom: '12px' }}>
                <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '4px' }}>Script:</p>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{emp.script}</p>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => setShowScript(emp)} className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}>
                  <Settings size={13} /> Edit Script
                </button>
                <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center', fontSize: '12px' }}>
                  <Phone size={13} /> Test Call
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreate && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }} onClick={() => setShowCreate(false)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="card" style={{ padding: '28px', width: '100%', maxWidth: '580px', maxHeight: '90vh', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>Create AI Employee</h2>
                <button onClick={() => setShowCreate(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={20} /></button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {/* URL Auto-Analyze */}
                <div style={{ padding: '16px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(6,182,212,0.05), rgba(6,182,212,0.1))', border: '1px solid rgba(6,182,212,0.2)' }}>
                  <p style={{ fontSize: '11px', fontWeight: '600', color: '#06b6d4', textTransform: 'uppercase', marginBottom: '8px' }}>Quick Setup - Paste Website URL</p>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '10px' }}>AI will read the website and auto-generate everything</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input type="url" placeholder="https://company-website.com" value={urlInput} onChange={e => setUrlInput(e.target.value)} className="input" style={{ flex: 1 }} />
                    <button onClick={analyzeURL} disabled={analyzingUrl || !urlInput.trim()} className="btn btn-primary" style={{ whiteSpace: 'nowrap', opacity: (analyzingUrl || !urlInput.trim()) ? 0.5 : 1 }}>
                      {analyzingUrl ? 'Analyzing...' : 'Auto-Fill'}
                    </button>
                  </div>
                </div>

                <div style={{ textAlign: 'center', fontSize: '11px', color: 'var(--text-dim)' }}>— or fill manually —</div>

                {/* Identity */}
                <p style={{ fontSize: '11px', fontWeight: '600', color: 'var(--accent-light)', textTransform: 'uppercase', marginTop: '8px' }}>Identity</p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <input type="text" placeholder="AI Name (e.g. Priya)" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className="input" />
                  <input type="text" placeholder="Role (e.g. AI Sales Executive)" value={form.role} onChange={e => setForm({...form, role: e.target.value})} className="input" />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <select value={form.industry} onChange={e => setForm({...form, industry: e.target.value})} className="input">
                    <option value="">Select Industry</option>
                    {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
                  </select>
                  <select value={form.voice} onChange={e => setForm({...form, voice: e.target.value})} className="input">
                    {VOICES.map(v => <option key={v.id} value={v.id}>{v.name} ({v.lang})</option>)}
                  </select>
                </div>
                <input type="text" placeholder="Languages (e.g. Telugu, Hindi, English)" value={form.languages} onChange={e => setForm({...form, languages: e.target.value})} className="input" />

                {/* Company */}
                <p style={{ fontSize: '11px', fontWeight: '600', color: 'var(--accent-light)', textTransform: 'uppercase', marginTop: '8px' }}>Company Info</p>
                <input type="text" placeholder="Company Name" value={form.company_name} onChange={e => setForm({...form, company_name: e.target.value})} className="input" />
                <textarea placeholder="Company details (products, services, pricing, location...)" value={form.company_info} onChange={e => setForm({...form, company_info: e.target.value})} className="input" style={{ height: '70px', resize: 'none' }} />

                {/* Script */}
                <p style={{ fontSize: '11px', fontWeight: '600', color: 'var(--accent-light)', textTransform: 'uppercase', marginTop: '8px' }}>Call Script</p>
                <input type="text" placeholder="Greeting (e.g. హాయ్! నేను Priya ని, ABC company నుంచి...)" value={form.greeting} onChange={e => setForm({...form, greeting: e.target.value})} className="input" />
                <textarea placeholder="Script: What should the AI talk about? (e.g. Sell 200 sq yard plot in Kondapur. Price 45L. Free registration offer until month end. Ask about budget and timeline.)" value={form.script} onChange={e => setForm({...form, script: e.target.value})} className="input" style={{ height: '100px', resize: 'none' }} />
                <textarea placeholder="Goals: What should AI achieve? (e.g. Qualify lead, Book site visit, Collect phone number)" value={form.goals} onChange={e => setForm({...form, goals: e.target.value})} className="input" style={{ height: '60px', resize: 'none' }} />

                <button onClick={createEmployee} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '14px', marginTop: '10px', fontSize: '14px' }}>
                  <Bot size={16} /> Create AI Employee
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Script Editor Modal */}
      <AnimatePresence>
        {showScript && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }} onClick={() => setShowScript(null)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="card" style={{ padding: '28px', width: '100%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>Edit Script — {showScript.name}</h2>
                <button onClick={() => setShowScript(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={20} /></button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Greeting (first thing AI says)</label>
                  <input type="text" value={showScript.greeting} onChange={e => setShowScript({...showScript, greeting: e.target.value})} className="input" />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Script (what AI should talk about)</label>
                  <textarea value={showScript.script} onChange={e => setShowScript({...showScript, script: e.target.value})} className="input" style={{ height: '150px', resize: 'vertical' }} />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Company Info</label>
                  <textarea value={showScript.company_info} onChange={e => setShowScript({...showScript, company_info: e.target.value})} className="input" style={{ height: '80px', resize: 'none' }} />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', display: 'block' }}>Goals</label>
                  <textarea value={showScript.goals} onChange={e => setShowScript({...showScript, goals: e.target.value})} className="input" style={{ height: '60px', resize: 'none' }} />
                </div>

                <button onClick={() => {
                  saveEmployees(employees.map(e => e.id === showScript.id ? showScript : e))
                  setShowScript(null)
                }} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px' }}>
                  Save Script
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
