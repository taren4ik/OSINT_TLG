FROM python:3.7.9-slim

WORKDIR /app

COPY . .

RUN pip3 install -r /app/requirements.txt --no-cache-dir


CMD ["python", "forward_messages_to_channel.py" ]

LABEL author='JGold' version=1.0