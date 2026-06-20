const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const tasksPanel = document.getElementById('tasks-panel');
const trashPanel = document.getElementById('trash-panel');
const openTrash = document.getElementById('open-trash');
const closeTrash = document.getElementById('close-trash');
const trashModal = document.getElementById('trash-modal');
const confirmModal = document.getElementById('confirm-modal');
const confirmText = document.getElementById('confirm-text');
const confirmYes = document.getElementById('confirm-yes');
const confirmNo = document.getElementById('confirm-no');

let pendingConfirmation = null;

function addMessage(text, type = 'bot') {
  const message = document.createElement('div');
  message.className = `message message--${type}`;
  message.textContent = text;
  chat.appendChild(message);
  chat.scrollTop = chat.scrollHeight;
}

function showReplies(replies) {
  replies.forEach(reply => addMessage(reply, 'bot'));
}

function renderTasks(tasks) {
  const activeTasks = tasks
    .map((task, index) => ({ ...task, _index: index }))
    .filter(task => !task.trashed);

  if (!activeTasks.length) {
    tasksPanel.textContent = 'Пока задач нет. Добавь задачу, и Добби сразу покажет её здесь.';
    return;
  }

  tasksPanel.innerHTML = '';
  activeTasks.forEach(task => {
    const node = document.createElement('div');
    node.className = 'task-item';
    node.innerHTML = `
      <div class="task-item__title">${task.title}</div>
      <div class="task-item__meta">
        <span>${task.icon}</span>
        <span>до ${new Date(task.deadline).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
      </div>
      <div class="task-controls">
        <button class="task-action" data-index="${task._index}" data-action="toggle">
          ${task.status === 'done' ? 'Вернуть в работу' : 'Выполнено'}
        </button>
        <button class="task-action task-action--delete" data-index="${task._index}" data-action="delete">
          Удалить задачу
        </button>
      </div>
    `;
    tasksPanel.appendChild(node);
  });
}

async function taskAction(index, action) {
  const response = await fetch('/api/task-action', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ index, action }),
  });

  if (!response.ok) {
    addMessage('Добби не смог выполнить действие с задачей. Попробуй еще раз.', 'bot');
    return;
  }

  const data = await response.json();
  showReplies(data.replies);
  renderTasks(data.tasks);
  renderTrash(data.tasks);
}

function showConfirm(message, callback) {
  pendingConfirmation = callback;
  confirmText.textContent = message;
  confirmModal.classList.remove('hidden');
}

function hideConfirm() {
  pendingConfirmation = null;
  confirmModal.classList.add('hidden');
}

confirmYes.addEventListener('click', () => {
  if (pendingConfirmation) {
    pendingConfirmation();
  }
  hideConfirm();
});

confirmNo.addEventListener('click', () => {
  hideConfirm();
});

openTrash.addEventListener('click', () => {
  trashModal.classList.remove('hidden');
});

closeTrash.addEventListener('click', () => {
  trashModal.classList.add('hidden');
});

trashModal.addEventListener('click', event => {
  if (event.target === trashModal) {
    trashModal.classList.add('hidden');
  }
});

function renderTrash(tasks) {
  const trashTasks = tasks
    .map((task, index) => ({ ...task, _index: index }))
    .filter(task => task.trashed);

  if (!trashTasks.length) {
    trashPanel.textContent = 'Корзина пуста. Удаленные задачи появятся здесь.';
    return;
  }

  trashPanel.innerHTML = '';
  trashTasks.forEach(task => {
    const node = document.createElement('div');
    node.className = 'trash-item';
    node.innerHTML = `
      <div class="trash-item__row">
        <div>
          <div class="task-item__title">${task.title}</div>
          <div class="task-item__meta">
            <span>${task.icon}</span>
            <span>до ${new Date(task.deadline).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
        <div class="task-controls">
          <button class="trash-action" data-action="restore" data-id="${task._index}">Восстановить</button>
          <button class="trash-action task-action--delete" data-action="destroy" data-id="${task._index}">Удалить совсем</button>
        </div>
      </div>
    `;
    trashPanel.appendChild(node);
  });
}

tasksPanel.addEventListener('click', event => {
  const button = event.target.closest('.task-action');
  if (!button) {
    return;
  }

  const index = Number(button.dataset.index);
  const action = button.dataset.action;
  if (Number.isNaN(index) || !action) {
    return;
  }

  if (action === 'delete') {
    showConfirm('Вы уверены, что хотите переместить задачу в корзину?', () => taskAction(index, 'trash'));
  } else {
    taskAction(index, action);
  }
});

trashPanel.addEventListener('click', event => {
  const button = event.target.closest('.trash-action');
  if (!button) {
    return;
  }

  const index = Number(button.dataset.id);
  const action = button.dataset.action;
  if (Number.isNaN(index) || !action) {
    return;
  }

  if (action === 'destroy') {
    showConfirm('Удалить задачу из корзины навсегда?', () => taskAction(index, 'destroy'));
  } else {
    taskAction(index, action);
  }
});

async function sendMessage(text) {
  addMessage(text, 'user');

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: text }),
  });

  if (!response.ok) {
    addMessage('Добби не смог связаться с сервером. Попробуй обновить страницу.', 'bot');
    return;
  }

  const data = await response.json();
  showReplies(data.replies);
  renderTasks(data.tasks);
}

async function loadTasks() {
  const response = await fetch('/api/tasks');
  if (!response.ok) {
    return;
  }
  const data = await response.json();
  renderTasks(data.tasks);
  renderTrash(data.tasks);
}

form.addEventListener('submit', event => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    return;
  }
  sendMessage(text);
  input.value = '';
});

addMessage('Добби очень рад видеть великого Мастера! Напиши команду: добавь задачу, покажи задачи, закрой задачу или игра.', 'bot');
loadTasks();

// Воспроизвести короткую сирену через WebAudio
function playSiren() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.setValueAtTime(800, ctx.currentTime);
    o.connect(g);
    g.connect(ctx.destination);
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.2, ctx.currentTime + 0.01);

    // Простая имитация сирены: частота меняется
    o.frequency.linearRampToValueAtTime(1200, ctx.currentTime + 0.25);
    o.frequency.linearRampToValueAtTime(600, ctx.currentTime + 0.5);
    o.start();
    setTimeout(() => {
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.02);
      o.stop(ctx.currentTime + 0.03);
      ctx.close();
    }, 600);
  } catch (e) {
    console.warn('Audio not available', e);
  }
}

// Опрос сервера на предмет новых уведомлений о просроченных задачах
async function pollNotifications() {
  try {
    const resp = await fetch('/api/notifications');
    if (!resp.ok) return;
    const data = await resp.json();
    if (!data.notifications || !data.notifications.length) return;
    data.notifications.forEach(n => {
      // Показать сообщение с эмодзи сирены и заголовком задачи
      showReplies([`${n.emoji} ${n.title} — Внимание!`]);
      playSiren();
    });
  } catch (e) {
    // молча игнорируем ошибки опроса
  }
}

setInterval(pollNotifications, 5000);
