import React, { useState } from 'react'
import { Form, Input, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../authContext'

const Register = () => {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const { register } = useAuth()

  const onFinish = async (values) => {
    try {
      await register(values.email, values.password)
      alert('Регистрация успешна!')
      navigate('/login')
    } catch (e) {
      alert('Ошибка регистрации')
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
      <Button type="primary" htmlType="submit" block>Зарегистрироваться</Button>
      <p style={{ marginTop: 16 }}>Уже есть аккаунт? <a href="/login">Войти</a></p>
    </Form>
  )
}

export default Register