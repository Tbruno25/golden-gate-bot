FROM python:3.9-slim-buster

WORKDIR /bot
COPY . .
RUN pip3 install -r requirements.txt

CMD python -u app.py