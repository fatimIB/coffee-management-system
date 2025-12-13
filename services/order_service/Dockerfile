FROM python:3.11-slim
WORKDIR /app

# Copy the service code
COPY ./services/order_service /app

# Copy the shared proto folder
COPY ./shared_proto /app/shared_proto

# Copy database connection
COPY ./database /app/database

RUN pip install --no-cache-dir -r requirements.txt

# Generate proto files if order_pb2 doesn't exist
RUN if [ ! -f /app/shared_proto/order_pb2.py ]; then \
    python -m grpc_tools.protoc -I/app/shared_proto --python_out=/app/shared_proto --grpc_python_out=/app/shared_proto /app/shared_proto/order.proto; \
    fi

EXPOSE 5002
CMD ["python", "app.py"]
