FROM python:3.11-slim
WORKDIR /app

COPY ./services/adminlogin /app

COPY ./shared_proto /app/shared_proto

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "app.py"]
