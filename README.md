#OSINT_CHAT_BOT - телеграм бот для получения информации об участниках чатов

Данный бот умеет извлекать статистическую информацию об участниках открытых чатов


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
bash
https://github.com/taren4ik/OSINT_TLG
cd OSINT_TLG
```

Cоздать и активировать виртуальное окружение:

```
bash
python -m venv venv
```

Для *nix-систем:
```
bash
source venv/bin/activate
```

Для windows-систем:
```
bash
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Создать файл .env и указать переменные окружения:

```
Получить при обращениии к @BotFather в Telegram
TOKEN 
Авторизоваться в Telegram по ссылке: https://my.telegram.org и перейти во 
вкладку 'API development tools'
API_ID
API_HASH 
```


Запустить проект:

```
bash
python osint_tlg.py
```
### При первом запуске потребуется подтвердить телефон для работы  клиента
#Please enter your phone (or bot token): 
#Please enter the code you received: 


***Над проектом работал:***
* Дмитрий Пермяков | Github:https://github.com/taren4ik  

