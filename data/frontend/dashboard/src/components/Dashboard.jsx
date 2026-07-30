import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { Users, Phone, Flame, Snowflake, Sun, TrendingUp, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import api from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_leads: 0, hot_leads: 0, warm_leads: 0, cold_leads: 0, total_calls: 0, conversion_rate: '0%'
  })

  useEffect(() => {
    api.get('/dashboard/stats').then(res => setStats(res.data)).catch(() => {})
  }, [])

  const metrics = [
    { label: 'Total Leads', value: stats.total_leads, change: '+12', up: true, icon: Users, color: '#22d3ee' },
    { label: 'Hot Leads', value: stats.hot_leads, change: '+3', up: true, icon: Flame, color: '#f87171' },
    { label: 'Warm Leads', value: stats.warm_leads, change: '+5', up: true, icon: Sun, color: '#fbbf24' },
    { label: 'Cold Leads', value: stats.cold_leads, change: '-2', up: false, icon: Snowflake, color: '#60a5fa' },
    { label: 'Calls Made', value: stats.total_calls, change: '+18', up: true, icon: Phone, color: '#34d399' },
    { label: 'Conversion', value: stats.conversion_rate, change: '+2.4%', up: true, icon: TrendingUp, color: '#06b6d4' },
  ]

  const weekData = [
    { day: 'Mon', calls: 14, qualified: 5 },
    { day: 'Tue', calls: 22, qualified: 9 },
    { day: 'Wed', calls: 11, qualified: 3 },
    { day: 'Thu', calls: 28, qualified: 12 },
    { day: 'Fri', calls: 18, qualified: 7 },
    { day: 'Sat', calls: 6, qualified: 2 },
    { day: 'Sun', calls: 3, qualified: 1 },
  ]

  const hourData = [
    { hour: '9am', calls: 5 },
    { hour: '10am', calls: 12 },
    { hour: '11am', calls: 18 },
    { hour: '12pm', calls: 8 },
    { hour: '1pm', calls: 4 },
    { hour: '2pm', calls: 15 },
    { hour: '3pm', calls: 22 },
    { hour: '4pm', calls: 16 },
    { hour: '5pm', calls: 9 },
  ]

  const recentActivity = [
    { name: 'Rahul Sharma', action: 'Qualified as hot lead', time: '2m ago', cat: 'hot' },
    { name: 'Priya Patel', action: 'Call completed successfully', time: '8m ago', cat: 'warm' },
    { name: 'Amit Kumar', action: 'Not interested - marked cold', time: '15m ago', cat: 'cold' },
    { name: 'Sneha Reddy', action: 'Follow-up scheduled', time: '22m ago', cat: 'warm' },
  ]

  return (
    <div>
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700', color: 'var(--text-primary)' }}>Overview</h1>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>Monitor your AI calling performance</p>
      </motion.div>

      {/* Stat Cards Grid - All 6 in one row on desktop */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '28px' }}>
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="stat-card"
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <m.icon size={16} color={m.color} />
              <span style={{ fontSize: '11px', fontWeight: '600', color: m.up ? '#34d399' : '#f87171', display: 'flex', alignItems: 'center', gap: '2px' }}>
                {m.up ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}
                {m.change}
              </span>
            </div>
            <p style={{ fontSize: '26px', fontWeight: '700', color: 'var(--text-primary)', lineHeight: 1 }}>{m.value}</p>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>{m.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts Row - Full width */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '12px', marginBottom: '28px' }}>
        {/* Area Chart */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>Weekly Performance</h3>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>Calls vs Qualified leads</p>
            </div>
            <div style={{ display: 'flex', gap: '16px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4' }}></span>Calls
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>Qualified
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={weekData}>
              <defs>
                <linearGradient id="gCalls" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gQual" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="day" stroke="var(--text-dim)" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-dim)" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px', color: 'var(--text-primary)' }} />
              <Area type="monotone" dataKey="calls" stroke="#06b6d4" strokeWidth={2} fill="url(#gCalls)" />
              <Area type="monotone" dataKey="qualified" stroke="#10b981" strokeWidth={2} fill="url(#gQual)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Bar Chart */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '4px' }}>Peak Hours</h3>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '20px' }}>Best time to call</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={hourData}>
              <XAxis dataKey="hour" stroke="var(--text-dim)" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--text-dim)" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px', color: 'var(--text-primary)' }} />
              <Bar dataKey="calls" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="card" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '16px' }}>Recent Activity</h3>
        <div>
          {recentActivity.map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: i < recentActivity.length - 1 ? '1px solid var(--border)' : 'none' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--accent-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: '600', color: 'var(--accent-light)' }}>
                  {item.name[0]}
                </div>
                <div>
                  <p style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-primary)' }}>{item.name}</p>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.action}</p>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className={`badge badge-${item.cat}`}>{item.cat}</span>
                <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
