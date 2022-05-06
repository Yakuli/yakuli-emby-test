FROM python:latest

WORKDIR '/root/emby'

RUN pip3 install python-telegram-bot requests

CMD python bot.py
