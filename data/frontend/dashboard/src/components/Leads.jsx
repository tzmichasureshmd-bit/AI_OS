import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Plus, Search, X, UserPlus, Upload, Download } from 'lucide-react'
import api from '../api'

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [form, setForm] = useState({ name: '', phone: '', email: '', company: '' })

  useEffect(() => { fetchLeads() }, [])

  const fetchLeads = async () => {
    try {
      const res = await api.get('/leads')
      setLeads(res.data.leads || [])
    } catch (err) {}
  }

  const addLead = async () => {
    if (!form.name || !form.phone) return
    await api.post('/leads', form).catch(() => {})
    setForm({ name: '', phone: '', email: '', company: '' })
    setShowModal(false)
    fetchLeads()
  }

  const uploadCSV = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await api.post('/leads/upload-csv', formData)
      alert(res.data.message)
      fetchLeads()
    } catch (err) {
      alert('Upload failed. Make sure CSV has: name, phone, email, company columns')
    }
    e.target.value = ''
  }

  const filtered = leads.filter(l => {
    const matchFilter = filter === 'all' || l.category === filter
    const matchSearch = l.name?.toLowerCase().includes(search.toLowerCase()) || l.phone?.includes(search)
    return matchFilter && matchSearch
  })

  return (
    <div>
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)' }}>Leads</h1>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>{leads.length} contacts in pipeline</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <a href="#" onClick={e => { e.preventDefault(); const base = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api'; window.open(`${base}/export/leads?client_id=${localStorage.getItem('client_id')}`) }} className="btn btn-ghost" style={{ textDecoration: 'none', cursor: 'pointer' }}>
            <Download size={14} /> Export
          </a>
          <label className="btn btn-ghost" style={{ cursor: 'pointer' }}>
            <Upload size={14} /> Upload CSV
            <input type="file" accept=".csv" onChange={uploadCSV} style={{ display: 'none' }} />
          </label>
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            <Plus size={14} /> Add Lead
          </button>
        </div>
      </motion.div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: '1', maxWidth: '280px' }}>
          <Search size={14} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input type="text" placeholder="Search leads..." value={search} onChange={e => setSearch(e.target.value)} className="input" style={{ paddingLeft: '36px' }} />
        </div>
        <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-input)', borderRadius: '9px', padding: '4px', border: '1px solid var(--border)' }}>
          {['all', 'hot', 'warm', 'cold'].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{ padding: '6px 14px', borderRadius: '6px', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', border: 'none', cursor: 'pointer', transition: 'all 0.15s', background: filter === f ? 'var(--accent-bg)' : 'transparent', color: filter === f ? 'var(--accent-light)' : 'var(--text-muted)' }}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {['Name', 'Phone', 'Company', 'Score', 'Category', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '14px 16px', fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '60px 0' }}>
                  <UserPlus size={28} style={{ color: 'var(--text-dim)', margin: '0 auto 12px' }} />
                  <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>No leads found</p>
                </td>
              </tr>
            ) : (
              filtered.map((lead, i) => (
                <motion.tr key={lead.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '30px', height: '30px', borderRadius: '7px', background: 'var(--accent-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: '600', color: 'var(--accent-light)' }}>
                        {lead.name?.[0]}
                      </div>
                      <div>
                        <p style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-primary)' }}>{lead.name}</p>
                        <p style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{lead.email || ''}</p>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: 'var(--text-secondary)' }}>{lead.phone}</td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: 'var(--text-muted)' }}>{lead.company || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '40px', height: '4px', borderRadius: '2px', background: 'var(--border)', overflow: 'hidden' }}>
                        <div style={{ height: '100%', borderRadius: '2px', background: '#06b6d4', width: `${lead.score * 10}%` }}></div>
                      </div>
                      <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-primary)' }}>{lead.score}</span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}><span className={`badge badge-${lead.category}`}>{lead.category}</span></td>
                  <td style={{ padding: '12px 16px', fontSize: '12px', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{lead.status}</td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }} onClick={() => setShowModal(false)}>
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }} onClick={e => e.stopPropagation()} className="card" style={{ padding: '28px', width: '100%', maxWidth: '400px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>New Lead</h2>
                <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}><X size={18} /></button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <input type="text" placeholder="Full Name *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="input" />
                <input type="text" placeholder="Phone *" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="input" />
                <input type="email" placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className="input" />
                <input type="text" placeholder="Company" value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} className="input" />
                <button onClick={addLead} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}>Add Lead</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
