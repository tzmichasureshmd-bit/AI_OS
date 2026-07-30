import { useState } from 'react'
import { ThemeProvider } from './ThemeContext'
import Login from './components/Login'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Leads from './components/Leads'
import CallSimulator from './components/CallSimulator'
import Campaigns from './components/Campaigns'
import CallLogs from './components/CallLogs'
import Profile from './components/Profile'
import AdminPanel from './components/AdminPanel'
import AIEmployees from './components/AIEmployees'
import Team from './components/Team'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [collapsed, setCollapsed] = useState(false)
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem('client_id'))
  const [clientData, setClientData] = useState(JSON.parse(localStorage.getItem('client_data') || '{}'))
  const [showAdmin, setShowAdmin] = useState(false)

  const handleLogin = (data) => {
    setClientData(data)
    setLoggedIn(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('client_id')
    localStorage.removeItem('client_data')
    setLoggedIn(false)
    setClientData({})
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />
      case 'ai-employees': return <AIEmployees />
      case 'leads': return <Leads />
      case 'calls': return <CallSimulator clientData={clientData} />
      case 'campaigns': return <Campaigns />
      case 'logs': return <CallLogs />
      case 'team': return <Team />
      case 'profile': return <Profile clientData={clientData} setClientData={setClientData} />
      default: return <Dashboard />
    }
  }

  if (!loggedIn) {
    return (
      <ThemeProvider>
        <Login onLogin={handleLogin} onAdmin={() => setShowAdmin(true)} />
      </ThemeProvider>
    )
  }

  if (showAdmin) {
    return (
      <ThemeProvider>
        <AdminPanel onBack={() => { setShowAdmin(false); window.location.hash = '' }} />
      </ThemeProvider>
    )
  }

  return (
    <ThemeProvider>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} collapsed={collapsed} setCollapsed={setCollapsed} onLogout={handleLogout} clientData={clientData} />
        <main style={{
          marginLeft: collapsed ? '68px' : '240px',
          width: collapsed ? 'calc(100% - 68px)' : 'calc(100% - 240px)',
          minHeight: '100vh',
          padding: '32px 40px',
          transition: 'all 0.3s cubic-bezier(0.68, -0.15, 0.27, 1.15)',
        }}>
          {renderPage()}
        </main>
      </div>
    </ThemeProvider>
  )
}

export default App
