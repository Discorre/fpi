import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'
import api from './api/api'

const AuthContext = createContext()

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const res = await api.get('http://localhost:8000/me')
      setUser(res.data)
    } catch (e) {
      //logout()
    }
    setLoading(false)
  }

  const login = async (email, password) => {
    try{
      const res = await axios.post('http://localhost:8000/auth/login', { email, password })
      const newToken = res.data.access_token
      const newRToken = res.data.refresh_token
      setToken(newToken)
      localStorage.setItem('token', newToken)
      localStorage.setItem('rtoken', newRToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      await fetchUser()
    } catch (e){
      alert(res.data.details)
    }

  }

  const register = async (email, password) => {
    await axios.post('http://localhost:8000/auth/register', { email, password })
  }

  const logout = (access_token, refresh_token) => {
    console.log(access_token, refresh_token);
    axios.post('http://localhost:8000/auth/logout', {refresh_token}, {
      headers: {
        'Authorization': `Bearer ${access_token}`,
      },
    });
    setUser(null)
    setToken('')
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    window.location.href = '/home';
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}