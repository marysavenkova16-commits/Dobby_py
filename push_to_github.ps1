# Запуск после установки Git
# Перейди в каталог проекта и выполни этот скрипт.

Set-Location "d:\Projects\codespaces-blank-main\codespaces-blank-main"

# Проверяем текущий статус
git status

# Установим основную ветку и добавим все изменения
git branch -M main
git add .
git commit -m "Add step-by-step task creation with deadline time and date"

# Пушим в указанный репозиторий
git push -u origin main

# Если потребуется аутентификация, используй GitHub Token или SSH ключ.
