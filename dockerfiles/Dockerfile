FROM python:3

WORKDIR /todoapp
COPY requirements.txt requirements.txt

RUN pip install -U pip && pip install -r requirements.txt && rm -rf /tmp/*

COPY src/ /todoapp

CMD ["python", "/todoapp/app.py"]
