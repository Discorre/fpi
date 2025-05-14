// Reviews.jsx
export default function Reviews() {
    return (
      <section className="reviews">
        <h2>Что говорят наши клиенты:</h2>
        <div className="review-list">
          <Review name="Виталий Заплатин" text="Оформил карту, а потом нашёл в договоре несколько мелких пакостей." />
          <Review name="Алексей Муткин" text="Почему-то я всегда в минусе. Магия?" />
          <Review name="Евгений Доверчив" text="Не понимаю, за что плачу. Но это и есть весь шарм." />
          <Review name="Николай Веритин" text="ФПИ — банк, который всегда рядом... особенно когда нужно снять комиссию." />
        </div>
      </section>
    )
  }
  
  function Review({ name, text }) {
    return (
      <div className="review">
        <p>“{text}”</p>
        <strong>— {name}</strong>
      </div>
    )
  }