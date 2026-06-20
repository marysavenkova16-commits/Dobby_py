from Dobby import handle_user_message, session_state, save_tasks, load_tasks

# Очистим состояние для теста
session_state['dialog_active'] = False
session_state['awaiting_intent'] = False
session_state['pending_task'] = None
session_state['pending_complete'] = False
session_state['waiting_for_spell'] = False

cases = [
    'Привет',
    'добавь задачу',
    'Помоги',
    'покажи задачи',
    'закрой задачу',
    'игра',
    'пока'
]

for msg in cases:
    replies, tasks = handle_user_message(msg)
    print('---')
    print('MSG:', msg)
    print('REPLIES:')
    for r in replies:
        print(' ', r)
