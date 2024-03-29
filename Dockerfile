# syntax=docker/dockerfile:1

FROM python:3.9-slim-bullseye

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm requirements.txt

COPY main.py main.py

CMD ["python", "main.py"]
