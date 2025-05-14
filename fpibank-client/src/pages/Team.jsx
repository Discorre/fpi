// Team.jsx
export default function Team() {
    const members = [
      { name: "Тимур Ловкачев", role: "Главный Архитектор Финансовых Пакостей" },
      { name: "Анатолий Обманов", role: "Главный Инженер По Финансовым Ловушкам" },
      { name: "Арсений Капканов", role: "Специалист По Неожиданным Платежам" },
      { name: "Павел Подвохов", role: "Специалист По Уловкам и Скрытым Опциям" },
      { name: "Лариса Загвоздкина", role: "Креативный Обдуролог" },
      { name: "Любовь Подвохова", role: "Креативный Уловкоплёт" },
      { name: "Аглая Вредникова", role: "Ведущий Консультант по Обдираловке" }
    ]
  
    return (
      <section className="team">
        <h2>Наша команда</h2>
        <div className="members">
          {members.map((member) => (
            <div key={member.name} className="member-card">
              <h3>👤 {member.name}</h3>
              <p><em>{member.role}</em></p>
            </div>
          ))}
        </div>
      </section>
    )
  }