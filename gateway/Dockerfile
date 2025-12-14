# Use Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy database connection module
COPY database /app/database

# Copy gateway app code
COPY gateway /app

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
