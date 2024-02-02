FROM python:3.11.4

ENV APP_HOME /app

WORKDIR /app

COPY . .

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
