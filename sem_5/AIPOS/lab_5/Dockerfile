FROM python:3.11-slim

WORKDIR /app

COPY . .


ENV MAIN_PORT=8000
ENV BASE_PORT=8001
ENV MAX_PORT=8100

CMD ["python", "main.py"]

