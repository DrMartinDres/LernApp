async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function loadStats() {
  const stats = await api('/api/stats');
  document.getElementById('stats').textContent = JSON.stringify(stats, null, 2);
}

async function loadReview() {
  const { cards } = await api('/api/cards');
  const now = new Date();
  const due = cards.filter(card => new Date(card.due_at) <= now);
  const review = document.getElementById('review');
  review.innerHTML = '';

  if (due.length === 0) {
    review.textContent = 'Aktuell keine fälligen Karten 🎉';
    return;
  }

  due.forEach((card) => {
    const box = document.createElement('div');
    box.className = 'review-card';
    box.innerHTML = `
      <strong>${card.subject}</strong><br/>
      <span>${card.front}</span><br/>
      <details><summary>Antwort anzeigen</summary>${card.back}</details>
      <div class="quality"></div>
    `;

    const qualityBox = box.querySelector('.quality');
    [0,1,2,3,4,5].forEach((q) => {
      const button = document.createElement('button');
      button.textContent = `Bewertung ${q}`;
      button.onclick = async () => {
        await api('/api/review', { method: 'POST', body: JSON.stringify({ card_id: card.id, quality: q }) });
        await loadReview();
        await loadStats();
      };
      qualityBox.appendChild(button);
    });
    review.appendChild(box);
  });
}

document.getElementById('card-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  await api('/api/cards', {
    method: 'POST',
    body: JSON.stringify({
      subject: form.get('subject'),
      front: form.get('front'),
      back: form.get('back'),
    }),
  });
  event.target.reset();
  await loadReview();
  await loadStats();
});

document.getElementById('agent-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  await api('/api/agents/generate-english-cards', {
    method: 'POST',
    body: JSON.stringify({
      topic: form.get('topic'),
      count: Number(form.get('count')),
    }),
  });
  await loadReview();
  await loadStats();
});

loadReview();
loadStats();
