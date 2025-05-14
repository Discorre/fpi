// src/components/Layout.jsx
import React from 'react'
import { Layout, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../authContext'

const { Header, Content } = Layout

const LayoutComponent = ({ children }) => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#fff' }}>
      <nav>
        <ul style={{ listStyle: 'none', display: 'flex', gap: '1rem' }}>
            <li><a href="/">Главная</a></li>
            <li><a href="/transfer">Перевести</a></li>
            <li><a href="/reviews">Отзывы</a></li>
            <li><a href="/commissions">Комиссии</a></li>
            <li><a href="/team">Команда</a></li>
        </ul>
      </nav>
        <h2 style={{ color: '#fff', margin: 0 }}>🏦 FPIBank</h2>
        {user && <Button onClick={() => logout()}>Выход</Button>}
      </Header>
      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: '1000px', margin: 'auto' }}>{children}</div>
      </Content>
    </Layout>
  )
}

export default LayoutComponent