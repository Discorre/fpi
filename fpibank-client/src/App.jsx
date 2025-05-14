import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Transfer from './pages/Transfer'
import { AuthProvider } from './authContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Reviews from './pages/Reviews'  
import Commissions from './pages/Commissions'
import Team from './pages/Team'
import ProtectedRoute from './components/ProtectedRoute'
import PublicOnlyRoute from './components/PublicOnlyRoute'

export const CartContext = React.createContext();

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            
            <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
            <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/transfer" element={<ProtectedRoute><Transfer /></ProtectedRoute>} />
            <Route path="/home" element={<Home />}/>
            <Route path="/reviews" element={<Reviews />} />
            <Route path="/commissions" element={<Commissions />} />
            <Route path="/team" element={<Team />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  )
}

export default App