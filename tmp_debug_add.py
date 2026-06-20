import Dobby

for msg in [
    'Добавь задачу купить молоко',
    'Добавь новую задачу купить молоко',
    'Новая задача купить молоко',
    'Добавь новую задачу'
]:
    Dobby.session_state['pending_task'] = None
    replies, tasks = Dobby.handle_user_message(msg)
    print('MSG:', msg)
    print('REPLIES:', replies)
    print('PENDING:', Dobby.session_state['pending_task'])
    print('---')
