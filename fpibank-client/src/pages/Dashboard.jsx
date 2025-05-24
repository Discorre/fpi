import React, { useEffect, useState } from 'react'
import { Card, Descriptions, Table, Button, Row, Col, Modal, Select, message } from 'antd'
import { useAuth } from '../authContext'
import { useNavigate } from 'react-router-dom'
import api from '../api/api'

const { Option } = Select
const API_URL = import.meta.env.VITE_API_BASE

const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [operations, setOperations] = useState([])
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [exchangeRates, setExchangeRates] = useState({
    USD_EUR: null,
    EUR_USD: null,
    USD_RUB: null,

  })
  const [selectedCurrency, setSelectedCurrency] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchOps = async () => {
      try {
        const res = await api.get(`${API_URL}/operations`)
        setOperations(res.data.operations || [])
      } catch (error) {
        console.error('Ошибка загрузки операций:', error)
        setOperations([])
      }
    }

    if (user) {
      fetchOps()
    }
  }, [user])

  //--- Загрузка курсов валют ---
  useEffect(() => {
    const fetchExchangeRates = async () => {
      try {
        const resUSDToEUR = await api.get(`${API_URL}/exchange-rate/USD/EUR`)
        const resEURToUSD = await api.get(`${API_URL}/exchange-rate/EUR/USD`)
        const resUSDToRUB = await api.get(`${API_URL}/exchange-rate/USD/RUB`)

        setExchangeRates({
          USD_EUR: resUSDToEUR.data.rate,
          EUR_USD: resEURToUSD.data.rate,
          USD_RUB: resUSDToRUB.data.rate,
        })
      } catch (error) {
        console.error('Ошибка загрузки курсов:', error)
      }
    }

    if (user) {
      fetchExchangeRates()
    }
  }, [user])

  const columns = [
      { title: 'Сумма', dataIndex: 'amount' },
      { title: 'Конвертировано', dataIndex: 'converted_amount' },
      { title: 'Из валюты', dataIndex: 'from_currency' },
      { title: 'В валюту', dataIndex: 'to_currency' },
      { title: 'Дата', dataIndex: 'at' }
    ]

  const showModal = () => setIsModalVisible(true)
  const handleCancel = () => setIsModalVisible(false)

  const handleCreateAccount = async () => {
    if (!selectedCurrency) {
      message.warning('Выберите валюту')
      return
    }

    setLoading(true)

    try {
      const response = await api.post(`${API_URL}/manage-account`, {
        action: 'add',
        currency: selectedCurrency,
      })

      message.success(response.data.message)
      setIsModalVisible(false)
      setSelectedCurrency('')
      window.location.reload() // можно обновить баланс без перезагрузки, если передадите его в user
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Ошибка при создании счёта'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card title="Мой профиль">
      <Row gutter={16}>
        <Col span={16}>
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Email">{user?.email}</Descriptions.Item>
            <Descriptions.Item label="Дата регистрации">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
            </Descriptions.Item>
            <Descriptions.Item label="Баланс">
              {Object.entries(user?.balances || {}).map(([curr, balance]) => (
                <div key={curr}>{balance} {curr}</div>
              ))}
              <Button onClick={showModal} block style={{ marginTop: 16 }}>
                Создать счёт
              </Button>
            </Descriptions.Item>
          </Descriptions>

          <Table dataSource={operations} columns={columns} rowKey="id" style={{ marginTop: 30 }} />

          <Button type="primary" onClick={() => navigate('/transfer')} block style={{ marginTop: 20 }}>
            Перевести
          </Button>
        </Col>

        <Col span={8}>
          <Card title="Текущие курсы валют">
            {exchangeRates.USD_EUR && <p>1 USD → {exchangeRates.USD_EUR} EUR</p>}
            {exchangeRates.EUR_USD && <p>1 EUR → {exchangeRates.EUR_USD} USD</p>}
            {exchangeRates.USD_RUB && <p>1 USD → {exchangeRates.USD_RUB} RUB</p>}
          </Card>
        </Col>
      </Row>
      {/* Модальное окно для выбора валюты */}
      <Modal
        title="Создать счёт"
        visible={isModalVisible}
        onOk={handleCreateAccount}
        onCancel={handleCancel}
        footer={[
          <Button key="back" onClick={handleCancel}>
            Отмена
          </Button>,
          <Button key="submit" type="primary" onClick={handleCreateAccount} loading={loading}>
            Создать
          </Button>
        ]}
      >
        <Select
          placeholder="Выберите валюту"
          onChange={(value) => setSelectedCurrency(value)}
          value={selectedCurrency}
          style={{ width: '100%' }}
        >
          {['USD', 'EUR', 'RUB'].map((curr) => (
            <Option key={curr} value={curr}>
              {curr}
            </Option>
          ))}
        </Select>
      </Modal>
    </Card>
  )
}

export default Dashboard