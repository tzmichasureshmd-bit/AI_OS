import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Phone, Clock, TrendingUp, Download } from 'lucide-react'
import api from '../api'

export default function CallLogs() {
  const [calls, setCalls] = useState([])

  useEffect(() => {
    api.get('/calls').then(res => setCalls(res.data.calls || [])).catch(() => {})
  }, [])

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)' }}>Call Logs</h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>{calls.length} calls recorded</p>
        </div>
        <a href="#" onClick={e => { e.preventDefault(); const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api'; window.open(`${base}/export/calls?client_id=${localStorage.getItem('client_id')}`) }} className="btn btn-ghost" style={{ textDecoration: 'none', cursor: 'pointer' }}>
          <Download size={14} /> Export Calls
        </a>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {calls.length === 0 ? (
          <div className="card" style={{ padding: '60px', textAlign: 'center' }}>
            <Phone size={28} style={{ color: 'var(--text-dim)', margin: '0 auto 12px' }} />
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No calls yet</p>
            <p style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>Use the Simulator to make your first call</p>
          </div>
        ) : (
          calls.map((call, i) => (
            <motion.div key={call.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }} className="card" style={{ padding: '16px 20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '9px', background: 'var(--accent-bg)', border: '1px solid var(--accent-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Phone size={14} color="var(--accent-light)" />
                  </div>
                  <div>
                    <p style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-primary)' }}>{call.lead_name}</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '3px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={10} /> {call.duration_seconds}s
                      </span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{call.sentiment}</span>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <TrendingUp size={12} color="var(--accent-light)" />
                    <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>{call.lead_score}/10</span>
                  </div>
                  <span className={`badge badge-${call.category}`}>{call.category}</span>
                </div>
              </div>
              {call.summary && (
                <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border)' }}>{call.summary}</p>
              )}
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}
