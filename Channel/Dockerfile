FROM python:3.7.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY test_forward.py .

CMD ["python", "test_forward.py"]

LABEL author="turgenevski@yandex.ru" version="1.2"
