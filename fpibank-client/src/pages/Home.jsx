// Home.jsx
import { Link } from 'react-router-dom'
import './styles/Home.css'

export default function Home() {
  return (
    <div className="home">
      <header className="hero">
        <h1>🏦 ФПИ Банк</h1>
        <p>Доверяйте нам, и мы всё уладим... как-нибудь!</p>
        <div className="cta">
          <Link to="/login"><button>Войти</button></Link>
          <Link to="/register"><button>Зарегистрироваться</button></Link>
        </div>
      </header>

      <section className="cards">
        <Card title="Пакости" icon="💥">
          Идеальный инструмент для тех, кто хочет добавить немного беспорядка в свои финансы.
        </Card>
        <Card title="Финансовая Ловушка" icon="🕸️">
          Каждый платеж может привести к скрытым комиссиям и загадкам.
        </Card>
        <Card title="СкрытаяКомиссияВКаждомПлатеже-инатор" icon="🧩">
          Каждый платеж превращается в грандиозное представление.
        </Card>
      </section>

      <section className="features">
        <h2>Наше приложение</h2>
        <ul>
          <li>🪄 Запутанный интерфейс</li>
          <li>💸 Автоматические сборы</li>
          <li>🎨 Абсурдный дизайн</li>
        </ul>
      </section>

      <footer>
        <p>© 2025 ФПИ-Банк. Все права случайно.</p>
      </footer>
    </div>
  )
}

function Card({ title, icon, children }) {
  return (
    <div className="card">
      <h3>{icon} {title}</h3>
      <p>{children}</p>
    </div>
  )
}