FROM python:3.11-slim
WORKDIR /app

COPY ./services/order_service /app

COPY ./shared_proto /app/shared_proto

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5002
CMD ["python", "app.py"]
