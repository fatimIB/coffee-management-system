FROM python:3.12-slim

WORKDIR /app

# Copy the service code
COPY ./services/cafe_service /app

# Copy the shared proto folder
COPY ./shared_proto /app/shared_proto

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "app.py"]
