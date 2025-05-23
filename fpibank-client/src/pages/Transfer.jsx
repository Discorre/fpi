import React, { useState } from 'react'
import { Form, Input, Select, Button } from 'antd'
import { useNavigate } from 'react-router-dom'

const currencies = ['USD', 'EUR', 'RUB']

const API_URL = import.meta.env.VITE_API_BASE

const Transfer = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const onFinish = async (values) => {
    try {
      const res = await fetch(`${API_URL}/transfer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(values)
      })
      if (res.ok) {
        alert('Перевод выполнен')
        navigate('/')
      } else {
      const data = await res.json();
      alert(data.detail || 'Ошибка перевода');
      }
    } catch (e) {
      alert('Ошибка сети')
    }
  }

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item label="Email получателя" name="target_email" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="Сумма" name="amount" rules={[{ required: true }]}>
        <Input type="number" />
      </Form.Item>
      <Form.Item label="Из валюты" name="from_currency" initialValue="USD">
        <Select options={currencies.map(c => ({ value: c, label: c }))} />
      </Form.Item>
      <Form.Item label="В валюту" name="to_currency" initialValue="EUR">
        <Select options={currencies.map(c => ({ value: c, label: c }))} />
      </Form.Item>
      <Button type="primary" htmlType="submit" block>Перевести</Button>
    </Form>
  )
}

export default Transfer