FROM python:3.11-slim
WORKDIR /app

# Copy the service code
COPY ./services/menu_service /app

# Copy the shared proto folder
COPY ./shared_proto /app/shared_proto


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
