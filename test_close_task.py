#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тест функционала закрытия задачи с подтверждением"""

import json
import os
from Dobby import handle_user_message, session_state, load_tasks, save_tasks, TASK_FILE

def test_close_task_workflow():
    """Тест полного цикла закрытия задачи"""
    
    # Очищаем состояние
    session_state['dialog_active'] = False
    session_state['awaiting_intent'] = False
    session_state['pending_complete'] = False
    session_state['pending_close_task'] = None
    session_state['awaiting_close_confirmation'] = False
    
    # Создаём тестовую задачу
    test_task = {
        'title': 'Помощь Гарри Поттеру',
        'deadline': '2026-06-25T18:00:00',
        'status': 'pending',
        'created': '2026-06-20T10:00:00'
    }
    
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump([test_task], f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("Тест 1: Команда 'закрой задачу' без названия")
    print("=" * 60)
    replies, _ = handle_user_message("закрой задачу")
    print(f"Ответ Добби: {replies[-1]}")
    print(f"Флаг dialog_active: {session_state['dialog_active']}")
    print(f"Флаг awaiting_intent: {session_state['awaiting_intent']}")
    print(f"Флаг pending_complete: {session_state['pending_complete']}")
    print()
    
    # Проверим, обработана ли команда правильно - должна быть просьба назвать задачу
    expected = 'Какую задачу нужно закрыть?'
    actual = replies[-1]
    if expected in actual:
        print("✅ Тест 1 ПРОЙДЕН: Добби просит назвать задачу для закрытия")
    else:
        print(f"❌ Тест 1 НЕ ПРОЙДЕН: Ожидалось '{expected}', получено '{actual}'")
    print()
    
    # Восстановим нужные флаги для следующего теста
    if not session_state['pending_complete']:
        session_state['pending_complete'] = True
    
    print("=" * 60)
    print("Тест 2: Ввод названия задачи для закрытия")
    print("=" * 60)
    replies, _ = handle_user_message("Помощь Гарри")
    print(f"Ответ Добби: {replies[-1]}")
    print(f"Флаг awaiting_close_confirmation: {session_state['awaiting_close_confirmation']}")
    print(f"Сохранённая задача: {session_state['pending_close_task']['title'] if session_state['pending_close_task'] else 'None'}")
    print()
    
    expected = 'Вы хотите закрыть задачу'
    actual = replies[-1]
    if expected in actual:
        print("✅ Тест 2 ПРОЙДЕН: Добби просит подтверждение")
    else:
        print(f"❌ Тест 2 НЕ ПРОЙДЕН: Ожидалось '{expected}', получено '{actual}'")
    print()
    
    print("=" * 60)
    print("Тест 3: Подтверждение закрытия (ответ 'да')")
    print("=" * 60)
    replies, tasks = handle_user_message("да")
    print(f"Ответ Добби: {replies[-1]}")
    print(f"Статус задачи после 'да': {tasks[0]['status']}")
    print(f"Флаг awaiting_close_confirmation: {session_state['awaiting_close_confirmation']}")
    print()
    
    if tasks[0]['status'] == 'done':
        print("✅ Тест 3 ПРОЙДЕН: Задача закрыта после подтверждения 'да'")
    else:
        print(f"❌ Тест 3 НЕ ПРОЙДЕН: Статус задачи не изменился")
    print()
    
    # Восстанавливаем состояние для второго теста
    session_state['dialog_active'] = False
    session_state['awaiting_intent'] = False
    session_state['pending_complete'] = False
    session_state['pending_close_task'] = None
    session_state['awaiting_close_confirmation'] = False
    
    test_task2 = {
        'title': 'Спасти Пленника Азкабана',
        'deadline': '2026-06-25T18:00:00',
        'status': 'pending',
        'created': '2026-06-20T10:00:00'
    }
    
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        json.dump([test_task2], f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("Тест 4: Команда 'закрой задачу' и отмена (ответ 'нет')")
    print("=" * 60)
    replies, _ = handle_user_message("закрой задачу")
    print(f"1. Добби просит задачу: {replies[-1]}")
    
    if not session_state['pending_complete']:
        session_state['pending_complete'] = True
    
    replies, _ = handle_user_message("Пленника")
    print(f"2. Добби просит подтверждение: {replies[-1]}")
    
    replies, tasks = handle_user_message("нет")
    print(f"3. Ответ Добби на 'нет': {replies[-1]}")
    print(f"Статус задачи после 'нет': {tasks[0]['status']}")
    print(f"Флаг awaiting_close_confirmation: {session_state['awaiting_close_confirmation']}")
    print()
    
    expected = 'Закрытие задачи отменяется.'
    actual = replies[-1]
    if expected == actual and tasks[0]['status'] == 'pending':
        print("✅ Тест 4 ПРОЙДЕН: Закрытие задачи отменено")
    else:
        print(f"❌ Тест 4 НЕ ПРОЙДЕН: Ожидалось '{expected}', получено '{actual}' или статус не 'pending'")
    print()
    
    # Очищаем тестовый файл
    if os.path.exists(TASK_FILE):
        os.remove(TASK_FILE)
    
    print("=" * 60)
    print("✅ Все тесты завершены!")
    print("=" * 60)

if __name__ == '__main__':
    test_close_task_workflow()

