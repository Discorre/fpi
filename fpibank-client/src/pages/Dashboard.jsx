import React, { useEffect, useState } from 'react'
import { Card, Descriptions, Table, Button } from 'antd'
import { useAuth } from '../authContext'
import { useNavigate } from 'react-router-dom'
import api from '../api/api'

const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [operations, setOperations] = useState([])

  useEffect(() => {
  const fetchOps = async () => {
    try {
      const res = await api.get('http://localhost:8000/operations');
      setOperations(res.data.operations || []);
    } catch (error) {
      console.error('Ошибка загрузки операций:', error);
      setOperations([]);
    }
  };

  if (user) {
    fetchOps();
  }
}, [user]);

  const columns = [
    { title: 'Сумма', dataIndex: 'amount' },
    { title: 'Конвертировано', dataIndex: 'converted_amount' },
    { title: 'Из валюты', dataIndex: 'from_currency' },
    { title: 'В валюту', dataIndex: 'to_currency' },
    { title: 'Дата', dataIndex: 'at' }
  ]

  return (
    <Card title="Мой профиль">
      <Descriptions bordered column={1}>
        <Descriptions.Item label="Email">{user?.email}</Descriptions.Item>
        <Descriptions.Item label="Дата регистрации">
          {user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
        </Descriptions.Item>
        <Descriptions.Item label="Баланс">
          {Object.entries(user?.balances || {}).map(([curr, balance]) => (
            <div key={curr}>{balance} {curr}</div>
          ))}
        </Descriptions.Item>
      </Descriptions>

      <Table dataSource={operations} columns={columns} rowKey="id" style={{ marginTop: 30 }} />

      <Button type="primary" onClick={() => navigate('/transfer')} block style={{ marginTop: 20 }}>
        Перевести
      </Button>
    </Card>
  )
}

export default Dashboard