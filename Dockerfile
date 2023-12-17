FROM python:3.7.9-slim

WORKDIR /app

COPY . .

RUN pip3 install -r /app/requirements.txt --no-cache-dir


CMD ["python", "channel_modul.py" ]

LABEL author='turgenevski@yandex.ru' version=1.2