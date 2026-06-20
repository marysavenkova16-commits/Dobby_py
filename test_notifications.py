from Dobby import load_tasks, save_tasks, check_for_newly_late_tasks, session_state
import datetime, os

# Добавим тестовую просроченную задачу
tasks = load_tasks()
# Удалим предыдущую тестовую запись, если была
tasks = [t for t in tasks if not t.get('title','').startswith('TEST_EXPIRED')]

expired = {
    'title': 'TEST_EXPIRED задача',
    'deadline': (datetime.datetime.now() - datetime.timedelta(minutes=1)).isoformat(),
    'status': 'pending',
    'created': datetime.datetime.now().isoformat()
}

tasks.append(expired)
save_tasks(tasks)

newly = check_for_newly_late_tasks()
print('Newly late:', [t['title'] for t in newly])

# Cleanup: mark test task as trashed
tasks = load_tasks()
for t in tasks:
    if t['title'].startswith('TEST_EXPIRED'):
        t['trashed'] = True
save_tasks(tasks)
print('Done')
