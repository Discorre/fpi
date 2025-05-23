import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'
import api from './api/api'

const AuthContext = createContext()
const API_URL = import.meta.env.VITE_API_BASE

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
      const res = await api.get(`${API_URL}/me`)
      setUser(res.data)
    } catch (e) {
      alert("Ошибка сервера")
    }
    setLoading(false)
  }

  const login = async (email, password) => {
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      const newToken = res.data.access_token;
      const newRToken = res.data.refresh_token;

      setToken(newToken);
      localStorage.setItem('token', newToken);
      localStorage.setItem('rtoken', newRToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      await fetchUser();

      return res.data;
    } catch (error) {
      let errorMessage = "Произошла ошибка при входе.";

      if (error.response?.data) {
        const errorData = error.response.data;

        if (Array.isArray(errorData.detail)) {
          const firstError = errorData.detail[0];
          if (firstError.loc && firstError.loc.length > 0) {
            const field = firstError.loc.slice(-1)[0];
            errorMessage = `Ошибка в поле "${field}": ${firstError.msg}`;
          } else {
            errorMessage = firstError.msg || "Ошибка валидации формы.";
          }
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      }

      alert(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const register = async (email, password) => {
    try {
      const res = await axios.post(`${API_URL}/auth/register`, { email, password });
      return res.data;
    } catch (error) {
      let errorMessage = "Произошла ошибка при регистрации.";

      // Проверяем, есть ли ответ от сервера
      if (error.response?.data) {
        const errorData = error.response.data;

        // Если это 422-ошибка (валидация Pydantic)
        if (Array.isArray(errorData.detail)) {
          // Берём первое сообщение из массива
          const firstError = errorData.detail[0];

          // Формируем сообщение: "Поле [email]: текст ошибки"
          if (firstError.loc && firstError.loc.length > 0) {
            const field = firstError.loc.slice(-1)[0]; // последнее значение пути
            errorMessage = `Ошибка в поле "${field}": ${firstError.msg}`;
          } else {
            errorMessage = firstError.msg || "Ошибка валидации формы.";
          }

        } else if (errorData.detail) {
          // Для других типов ошибок (например, уникальность email)
          errorMessage = errorData.detail;
        }
      }

      alert(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const logout = (access_token, refresh_token) => {
    console.log(access_token, refresh_token);
    axios.post(`${API_URL}/auth/logout`, {refresh_token}, {
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