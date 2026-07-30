import { motion } from 'framer-motion'
import { useState } from 'react'
import { Zap, Lock, UserPlus, Eye, EyeOff, Building, Users, Shield } from 'lucide-react'
import axios from 'axios'

const API = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api'

export default function Login({ onLogin, onAdmin }) {
  const [mode, setMode] = useState('login') // login, register, team
  const [loginType, setLoginType] = useState('client') // client, team, admin
  const [error, setError] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [adminTaps, setAdminTaps] = useState(0)

  // Secret: Tap logo 5 times to open Super Admin
  const handleLogoTap = () => {
    const taps = adminTaps + 1
    setAdminTaps(taps)
    if (taps >= 5) {
      const key = prompt('Enter Admin Key:')
      if (key === 'superadmin123') onAdmin()
      else if (key) alert('Invalid key')
      setAdminTaps(0)
    }
    setTimeout(() => setAdminTaps(0), 3000) // reset after 3 sec
  }

  const [reg, setReg] = useState({ company_name: '', industry: '', contact_name: '', email: '', phone: '', password: '', product_info: '', ai_name: 'Alex' })

  const handleClientLogin = async () => {
    if (!email || !password) return setError('Fill all fields')
    setLoading(true)
    try {
      const res = await axios.post(`${API}/auth/login`, { email, password })
      localStorage.setItem('client_id', res.data.client_id)
      localStorage.setItem('client_data', JSON.stringify(res.data))
      localStorage.setItem('user_role', 'client_admin')
      onLogin(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
    setLoading(false)
    setTimeout(() => setError(''), 3000)
  }

  const handleTeamLogin = async () => {
    if (!email || !password) return setError('Fill all fields')
    setLoading(true)
    try {
      const res = await axios.post(`${API}/auth/team-login`, { email, password })
      localStorage.setItem('client_id', res.data.client_id)
      localStorage.setItem('client_data', JSON.stringify(res.data))
      localStorage.setItem('user_role', res.data.role)
      localStorage.setItem('user_permissions', res.data.permissions)
      onLogin(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
    setLoading(false)
    setTimeout(() => setError(''), 3000)
  }

  const handleAdminLogin = () => {
    if (adminKey === 'superadmin123') {
      onAdmin()
    } else {
      setError('Invalid admin key')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleRegister = async () => {
    if (!reg.company_name || !reg.email || !reg.password || !reg.product_info) return setError('Fill required fields')
    if (!reg.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/)) return setError('Enter a valid email address')
    if (reg.password.length < 6) return setError('Password must be at least 6 characters')
    setLoading(true)
    try {
      await axios.post(`${API}/auth/register`, reg)
      setMode('login')
      setEmail(reg.email)
      alert('Registration successful! Please login.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    }
    setLoading(false)
    setTimeout(() => setError(''), 3000)
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)', padding: '20px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card" style={{ padding: '36px', width: '100%', maxWidth: mode === 'register' ? '440px' : '400px' }}>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div onClick={handleLogoTap} style={{ width: '50px', height: '50px', borderRadius: '12px', background: 'linear-gradient(135deg, #06b6d4, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px', cursor: 'pointer', userSelect: 'none' }}>
            <Zap size={22} color="white" />
          </div>
          <h1 style={{ fontSize: '18px', fontWeight: '700', color: 'var(--text-primary)' }}>AI Caller</h1>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {mode === 'register' ? 'Create your company account' : 'Sign in to continue'}
          </p>
        </div>

        {/* LOGIN MODE */}
        {mode === 'login' && (
          <>
            {/* Login Type Tabs */}
            <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-input)', borderRadius: '10px', padding: '4px', marginBottom: '20px' }}>
              {[
                { id: 'client', label: 'Company', icon: Building },
                { id: 'team', label: 'Team', icon: Users },
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => { setLoginType(tab.id); setError('') }}
                  style={{
                    flex: 1,
                    padding: '8px 4px',
                    borderRadius: '7px',
                    fontSize: '11px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    background: loginType === tab.id ? 'var(--accent-bg)' : 'transparent',
                    color: loginType === tab.id ? '#06b6d4' : 'var(--text-muted)',
                    border: loginType === tab.id ? '1px solid var(--accent-border)' : '1px solid transparent',
                  }}
                >
                  <tab.icon size={12} /> {tab.label}
                </button>
              ))}
            </div>

            {/* Client / Team Login */}
            {(loginType === 'client' || loginType === 'team') && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} onKeyDown={e => e.key === 'Enter' && (loginType === 'client' ? handleClientLogin() : handleTeamLogin())} className="input" />
                <div style={{ position: 'relative' }}>
                  <input type={showPass ? 'text' : 'password'} placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === 'Enter' && (loginType === 'client' ? handleClientLogin() : handleTeamLogin())} className="input" style={{ paddingRight: '40px' }} />
                  <button onClick={() => setShowPass(!showPass)} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                    {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
                {error && <p style={{ fontSize: '11px', color: '#f87171', textAlign: 'center' }}>{error}</p>}
                <button onClick={loginType === 'client' ? handleClientLogin : handleTeamLogin} disabled={loading} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '6px', opacity: loading ? 0.6 : 1 }}>
                  <Lock size={14} /> {loading ? 'Signing in...' : 'Sign In'}
                </button>
              </div>
            )}

            {/* Register link */}
            {loginType === 'client' && (
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '16px' }}>
                New company? <span onClick={() => setMode('register')} style={{ color: '#06b6d4', cursor: 'pointer', fontWeight: '600' }}>Register here</span>
              </p>
            )}
          </>
        )}

        {/* REGISTER MODE */}
        {mode === 'register' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input type="text" placeholder="Company Name *" value={reg.company_name} onChange={e => setReg({...reg, company_name: e.target.value})} className="input" />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <input type="text" placeholder="Your Name *" value={reg.contact_name} onChange={e => setReg({...reg, contact_name: e.target.value})} className="input" />
              <select value={reg.industry} onChange={e => setReg({...reg, industry: e.target.value})} className="input">
                <option value="">Industry *</option>
                <option value="education">Education</option>
                <option value="real_estate">Real Estate</option>
                <option value="insurance">Insurance</option>
                <option value="healthcare">Healthcare</option>
                <option value="finance">Finance</option>
                <option value="ecommerce">E-Commerce</option>
                <option value="saas">SaaS/Tech</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <input type="email" placeholder="Email *" value={reg.email} onChange={e => setReg({...reg, email: e.target.value})} className="input" />
              <input type="text" placeholder="Phone" value={reg.phone} onChange={e => setReg({...reg, phone: e.target.value})} className="input" />
            </div>
            <div style={{ position: 'relative' }}>
              <input type={showPass ? 'text' : 'password'} placeholder="Password *" value={reg.password} onChange={e => setReg({...reg, password: e.target.value})} className="input" style={{ paddingRight: '40px' }} />
              <button onClick={() => setShowPass(!showPass)} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            <textarea placeholder="What does your company offer? *" value={reg.product_info} onChange={e => setReg({...reg, product_info: e.target.value})} className="input" style={{ height: '70px', resize: 'none' }} />
            <input type="text" placeholder="AI Caller Name (default: Alex)" value={reg.ai_name} onChange={e => setReg({...reg, ai_name: e.target.value})} className="input" />
            {error && <p style={{ fontSize: '11px', color: '#f87171', textAlign: 'center' }}>{error}</p>}
            <button onClick={handleRegister} disabled={loading} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '6px', opacity: loading ? 0.6 : 1 }}>
              <UserPlus size={14} /> {loading ? 'Creating...' : 'Create Account'}
            </button>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '12px' }}>
              Already registered? <span onClick={() => setMode('login')} style={{ color: '#06b6d4', cursor: 'pointer', fontWeight: '600' }}>Sign In</span>
            </p>
          </div>
        )}
      </motion.div>
    </div>
  )
}
