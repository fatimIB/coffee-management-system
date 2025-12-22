FROM python:3.11-slim
WORKDIR /app

# Copy the service code
COPY ./services/login_service /app

# Copy the shared proto folder
COPY ./shared_proto /app/shared_proto

RUN pip install --default-timeout=500 --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]