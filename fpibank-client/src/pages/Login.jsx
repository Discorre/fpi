import React, { useState } from 'react'
import { Form, Input, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../authContext'

const Login = () => {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const { login } = useAuth()

  const onFinish = async (values) => {
    try {
      await login(values.email, values.password)
      navigate('/')
    } catch (e) {
      alert('Ошибка авторизации');
    }
  }

  return (
    <Form form={form} onFinish={onFinish} layout="vertical">
      <Form.Item label="Email" name="email" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="Пароль" name="password" rules={[{ required: true }]}>
        <Input.Password />
      </Form.Item>
      <Button type="primary" htmlType="submit" block>Войти</Button>
      <p style={{ marginTop: 16 }}>Нет аккаунта? <a href="/register">Зарегистрироваться</a></p>
    </Form>
  )
}

export default Login