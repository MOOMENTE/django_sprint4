# django_sprint4
Платформа для блогов.
Позволяет вести собственный блог и читать блоги других пользователей.
## Стек:
Python, Django
## Запуск отладочного сервера под windows:
В директории с проектом
1. Создание виртуального окружения:
```commandline
python -m venv venv
```
2. Активация виртуального окружения:
```commandline
source venv\Scripts\activate  
```
Если возникла ошибка 'Имя "source" не распознано' или аналогичная:
```commandline
venv\Scripts\activate
```
3. Установка зависимостей:
```commandline
pip install -r requirements.txt
```
4. Запуск отладочного сервера:
```commandline
cd blogicum
python manage.py runserver
```
