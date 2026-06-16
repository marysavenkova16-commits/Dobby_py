import json
import datetime
import random
import re
import os
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_FILE = os.path.join(BASE_DIR, 'tasks.json')
PORT = 8000

session_state = {
    'waiting_for_spell': False,
    'bonus_frogs': 0,
    'pending_task': None,
}

# Загрузка списка задач из файла. Если файла нет — возвращаем пустой список.
def load_tasks():
    try:
        with open(TASK_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Сохранение списка задач в файл.
def save_tasks(tasks):
    with open(TASK_FILE, 'w', encoding='utf-8') as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)

# Преобразование строки в дедлайн. Поддерживаем формат "через 30 минут" и просто число минут.
def parse_deadline(text):
    text = text.strip().lower()
    match = re.search(r'через\s*(\d+)\s*час', text)
    if match:
        return datetime.datetime.now() + datetime.timedelta(hours=int(match.group(1)))

    match = re.search(r'через\s*(\d+)\s*мин', text)
    if match:
        return datetime.datetime.now() + datetime.timedelta(minutes=int(match.group(1)))

    match = re.search(r'^(\d+)\s*$', text)
    if match:
        return datetime.datetime.now() + datetime.timedelta(minutes=int(match.group(1)))

    match = re.search(r'^(\d+)\s*мин', text)
    if match:
        return datetime.datetime.now() + datetime.timedelta(minutes=int(match.group(1)))

    raise ValueError('Добби не понял, когда дедлайн.')

# Парсим время дедлайна для пошагового ввода.
def parse_deadline_time(text):
    text = text.strip().lower()
    match = re.search(r'^(\d{1,2})\s*[:\.]\s*(\d{2})$', text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if 0 <= hour < 24 and 0 <= minute < 60:
            return {'hour': hour, 'minute': minute}

    match = re.search(r'^(\d{1,2})\s*час(?:а|ов)?$', text)
    if match:
        hour = int(match.group(1))
        if 0 <= hour < 24:
            return {'hour': hour, 'minute': 0}

    match = re.search(r'^(\d{1,2})$', text)
    if match:
        hour = int(match.group(1))
        if 0 <= hour < 24:
            return {'hour': hour, 'minute': 0}

    raise ValueError('Добби не понял время. Напиши, например, 18:30 или 9.')

# Парсим дату дедлайна для пошагового ввода.
def parse_deadline_date(text, time_info):
    text = text.strip().lower()
    now = datetime.datetime.now()
    today = now.date()

    if 'послезавтра' in text:
        deadline_date = today + datetime.timedelta(days=2)
    elif 'завтра' in text:
        deadline_date = today + datetime.timedelta(days=1)
    elif 'сегодня' in text:
        deadline_date = today
    else:
        # Оставляем только дату из текста, извлекая числа и разделители.
        match = re.search(r'^(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?$', text)
        if not match:
            raise ValueError('Добби не понял дату. Напиши, например, 16.06 или завтра.')

        day = int(match.group(1))
        month = int(match.group(2))
        year = match.group(3)
        if year:
            year = int(year)
            if year < 100:
                year += 2000
        else:
            year = today.year

        try:
            deadline_date = datetime.date(year, month, day)
        except ValueError:
            raise ValueError('Добби не понял дату. Укажи правильную дату.')

        if deadline_date < today:
            deadline_date = datetime.date(year + 1, month, day)

    return datetime.datetime(
        deadline_date.year,
        deadline_date.month,
        deadline_date.day,
        time_info['hour'],
        time_info['minute']
    )

# Отметки статуса для вывода.
def get_status_icon(task):
    if task['status'] == 'done':
        return '✅ Выполнено'
    if task['status'] == 'late':
        return '🚨 ПРОСРОЧЕНО'
    return '⏳ Ожидает'

# Проверяем просроченные задачи при каждом действии.
def check_for_late_tasks(tasks):
    now = datetime.datetime.now()
    updated = False
    for task in tasks:
        if task['status'] == 'pending':
            try:
                deadline = datetime.datetime.fromisoformat(task['deadline'])
            except ValueError:
                continue
            if now > deadline:
                task['status'] = 'late'
                updated = True
    if updated:
        save_tasks(tasks)
    return [task for task in tasks if task['status'] == 'late']

# Формируем текстовое описание задач для чат-сообщения.
def describe_tasks(tasks):
    if not tasks:
        return 'Пока задач нет. Добби готов слушать великий Мастер.'

    lines = ['Список задач Добби:']
    for index, task in enumerate(tasks, start=1):
        status = get_status_icon(task)
        deadline = datetime.datetime.fromisoformat(task['deadline']).strftime('%Y-%m-%d %H:%M')
        lines.append(f'{index}. {task["title"]} — {status} (до {deadline})')
    return '\n'.join(lines)

# Добавление задачи из текстовой команды.
def get_task_title_from_message(message):
    title = re.sub(r'\b(добавь|добави|добавить|новая|новую|новой|нов|запис|поставь|задачу|задач)\b', '', message, flags=re.IGNORECASE).strip(' .,-')
    return title or None

def create_task(title, deadline, tasks):
    task = {
        'title': title,
        'deadline': deadline.isoformat(),
        'status': 'pending',
        'created': datetime.datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return f'Добби все сделал! Задача "{task["title"]}" добавлена, и Добби уже волнуется за дедлайн.'

def add_task_from_message(message, tasks):
    deadline_match = re.search(r'через\s*\d+\s*(час|часа|часов|минут|мин)', message)
    numeric_match = re.search(r'(\d+)\s*$', message)
    title = message
    deadline_text = None
    if deadline_match:
        deadline_text = deadline_match.group(0)
        title = message.replace(deadline_text, '')
    elif numeric_match:
        deadline_text = numeric_match.group(0)
        title = message[:numeric_match.start()].strip()

    title = get_task_title_from_message(title)

    if deadline_text:
        if not title:
            title = 'задание от Мастера'
        deadline = parse_deadline(deadline_text)
        return create_task(title, deadline, tasks)

    if not title:
        session_state['pending_task'] = {'stage': 'title'}
        return 'Как называется задача?'

    session_state['pending_task'] = {
        'stage': 'time',
        'title': title
    }
    return 'Напиши время дедлайна. Например 18:30 или 9.'

def handle_pending_task(message, tasks):
    pending = session_state.get('pending_task') or {}
    stage = pending.get('stage')
    if stage == 'title':
        title = message.strip()
        if not title:
            raise ValueError('Добби не услышал название задачи. Назови, пожалуйста, задачу.')
        session_state['pending_task'] = {
            'stage': 'time',
            'title': title
        }
        return ['Напиши время дедлайна. Например 18:30 или 9.'], tasks

    if stage == 'time':
        time_info = parse_deadline_time(message)
        session_state['pending_task'] = {
            'stage': 'date',
            'title': pending['title'],
            'time': time_info
        }
        return ['Дату дедлайна, пожалуйста. Например 16.06.2026, 16.06 или завтра.'], tasks

    if stage == 'date':
        time_info = pending.get('time')
        if not time_info:
            raise ValueError('Произошла ошибка. Напиши время дедлайна еще раз.')
        deadline = parse_deadline_date(message, time_info)
        title = pending.get('title') or 'задание от Мастера'
        session_state['pending_task'] = None
        return [create_task(title, deadline, tasks)], tasks

    return ['Добби не уверен, что делать дальше. Скажи: добавь задачу, покажи задачи, выполнил задачу или игра.'], tasks

# Завершение задачи по команде.
def complete_task_from_message(message, tasks):
    query = message.lower()
    index_match = re.search(r'\d+', query)
    chosen = None
    if index_match:
        index = int(index_match.group(0)) - 1
        if 0 <= index < len(tasks):
            chosen = tasks[index]

    if not chosen:
        for task in tasks:
            if task['title'].lower() in query or query in task['title'].lower():
                chosen = task
                break

    if not chosen:
        raise ValueError('Добби не нашел задачу. Назови номер или часть названия.')

    if chosen['status'] == 'done':
        return 'Добби уже отмечал эту задачу выполненной. Мастер очень внимателен!'

    chosen['status'] = 'done'
    save_tasks(tasks)
    return 'О, как хорошо! Добби так старался, что у него слезы счастья на глазах.'

# Игровая магическая дуэль.
def resolve_spell_duel(choice, tasks):
    spells = {
        'экспеллиармус': 'протего',
        'ступефай': 'экспеллиармус',
        'протего': 'ступефай'
    }
    spell_names = list(spells.keys())
    if choice not in spell_names:
        raise ValueError('Добби не понял заклинание. Скажи Экспеллиармус, Ступефай или Протего.')

    bot_choice = random.choice(spell_names)
    reply = [f'Добби выбрал {bot_choice.capitalize()}!']
    if choice == bot_choice:
        reply.append('Ох, ничья! Добби слегка вздрогнул от волнения.')
        return '\n'.join(reply)

    if spells[choice] == bot_choice:
        reply.append('Ура! Добби победил! Добби визжит от радости и очень надеется на похвалу.')
        late_tasks = [task for task in tasks if task['status'] == 'late']
        if late_tasks:
            forgiven = late_tasks[0]
            forgiven['status'] = 'done'
            save_tasks(tasks)
            reply.append(f'Добби прощает задачу "{forgiven["title"]}". Она теперь считается выполненной.')
        else:
            session_state['bonus_frogs'] += 1
            reply.append('Добби дарит тебе виртуальную шоколадную лягушку! У Добби теперь еще больше добрых мыслей.')
        return '\n'.join(reply)

    reply.append('Ой, простите, Мастер, Добби случайно чихнул и сбил прицел!')
    return '\n'.join(reply)

# Обработка сообщений пользователя и генерация диалоговых реплик.
def handle_user_message(message):
    tasks = load_tasks()
    replies = []
    late_tasks = check_for_late_tasks(tasks)
    if late_tasks:
        replies.append('Добби в панике! Есть просроченные задачи!')
        for task in late_tasks:
            replies.append(f' - {task["title"]} (прошел срок)')
        replies.append('Добби боится, что Мастер даст ему носок. Пожалуйста, помоги Добби!')

    text = message.strip().lower()
    if not text:
        replies.append('Добби слушает, добрый Мастер. Напиши команду.')
        return replies, tasks

    if session_state['waiting_for_spell']:
        if any(spell in text for spell in ('экспеллиармус', 'ступефай', 'протего')):
            spell = next(spell for spell in ('экспеллиармус', 'ступефай', 'протего') if spell in text)
            replies.append(resolve_spell_duel(spell, tasks))
            session_state['waiting_for_spell'] = False
            return replies, tasks
        replies.append('Добби ждет заклинание: Экспеллиармус, Ступефай или Протего.')
        return replies, tasks

    if session_state.get('pending_task'):
        pending_replies, tasks = handle_pending_task(message.strip(), tasks)
        replies.extend(pending_replies)
        return replies, tasks

    # Проверяем выход ТОЛЬКО если это точное слово "пока", не часть другого слова
    if re.search(r'^пока\b|[^а-яё]пока\b', text):
        replies.append('Добби грустит, но будет ждать следующего задания. Возвращайтесь скорее, великий Мастер!')
        return replies, tasks

    try:
        if re.search(r'\b(добавь|добави|добавить|новая|новую|новой|нов|запис|поставь)\b', text):
            replies.append(add_task_from_message(text, tasks))
            return replies, tasks

        if re.search(r'\b(показать|покажи|список|задачи)\b', text):
            replies.append(describe_tasks(tasks))
            return replies, tasks

        if re.search(r'\b(выполнить|сделал|готово|закрыть)\b', text):
            replies.append(complete_task_from_message(text, tasks))
            return replies, tasks

        if re.search(r'\b(игра|дуэль|магия)\b', text):
            session_state['waiting_for_spell'] = True
            replies.append('Добби готовится к магической дуэли! Назови заклинание: Экспеллиармус, Ступефай или Протего.')
            return replies, tasks

        if re.search(r'\b(шоколад|лягушка)\b', text):
            replies.append(f'У тебя {session_state["bonus_frogs"]} шоколадных лягушек. Добби очень горд!')
            return replies, tasks

        replies.append('Добби не совсем понял этого. Скажи: добавь задачу, покажи задачи, выполнил задачу или игра.')
    except ValueError as error:
        replies.append(str(error))
    except Exception:
        replies.append('Ой! Добби чуть не потерялся в своих мыслях. Повтори, пожалуйста, команду.')

    return replies, tasks

class DobbyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/tasks':
            tasks = load_tasks()
            check_for_late_tasks(tasks)
            response = {
                'tasks': [
                    {
                        'title': task['title'],
                        'deadline': task['deadline'],
                        'status': task['status'],
                        'icon': get_status_icon(task),
                        'trashed': task.get('trashed', False)
                    }
                    for task in tasks
                ]
            }
            response_body = json.dumps(response, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            return

        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/task-action':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                payload = json.loads(body)
                index = payload.get('index')
                action = payload.get('action')
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
                return

            tasks = load_tasks()
            if not isinstance(index, int) or index < 0 or index >= len(tasks):
                self.send_error(400, 'Invalid task index')
                return

            task = tasks[index]
            if action == 'toggle':
                task['status'] = 'pending' if task['status'] == 'done' else 'done'
                save_tasks(tasks)
                replies = [
                    'Добби обновил задачу.',
                    'Задача теперь ' + ('возвращена в работу.' if task['status'] == 'pending' else 'отмечена как выполненная.')
                ]
            elif action == 'trash':
                task['trashed'] = True
                save_tasks(tasks)
                replies = [f'Добби переместил задачу "{task["title"]}" в корзину.']
            elif action == 'restore':
                task['trashed'] = False
                save_tasks(tasks)
                replies = [f'Добби восстановил задачу "{task["title"]}" из корзины.']
            elif action == 'destroy':
                title = task['title']
                tasks.pop(index)
                save_tasks(tasks)
                replies = [f'Добби удалил задачу "{title}" навсегда.']
            else:
                self.send_error(400, 'Invalid action')
                return

            response = {
                'replies': replies,
                'tasks': [
                    {
                        'title': t['title'],
                        'deadline': t['deadline'],
                        'status': t['status'],
                        'icon': get_status_icon(t),
                        'trashed': t.get('trashed', False)
                    }
                    for t in tasks
                ],
                'bonus': session_state['bonus_frogs']
            }

            response_body = json.dumps(response, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            return

        if self.path != '/api/chat':
            self.send_error(404, 'Not found')
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body)
            message = payload.get('message', '')
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            return

        replies, tasks = handle_user_message(message)
        response = {
            'replies': replies,
            'tasks': [
                {
                    'title': task['title'],
                    'deadline': task['deadline'],
                    'status': task['status'],
                    'icon': get_status_icon(task),
                    'trashed': task.get('trashed', False)
                }
                for task in tasks
            ],
            'bonus': session_state['bonus_frogs']
        }

        response_body = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)


def run_server():
    os.chdir(BASE_DIR)
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DobbyHandler)
    print(f'Добби ждет великого Мастера на сайте: http://localhost:{PORT}/')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nДобби закрывает браузер и ждет снова, если Мастер вернется.')

if __name__ == '__main__':
    run_server()
