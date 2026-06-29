@echo off
call .venv\Scripts\activate.bat
cd /d "C:\My Files\Sayem\MySoft\debtcollection\backend"
python manage.py runserver
pause

