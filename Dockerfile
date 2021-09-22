# syntax=docker/dockerfile:1

FROM python:3.9-slim-bullseye

RUN pip install requests

COPY main.py main.py

CMD ["python", "main.py"]
