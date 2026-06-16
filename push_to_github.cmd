@echo off
cd /d "d:\Projects\codespaces-blank-main\codespaces-blank-main"

echo Проверка статуса репозитория...
git status

echo Подготавливаем коммит...
git branch -M main
git add .
git commit -m "Add step-by-step task creation with deadline time and date"

echo Пушим в origin main...
git push -u origin main

echo Готово. Если возникли ошибки, убедитесь, что Git установлен и настроен.
pause
