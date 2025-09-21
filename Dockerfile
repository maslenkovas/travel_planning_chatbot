# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only dependency files first
COPY pyproject.toml /app/

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir .

# Copy project files
COPY . /app

# Expose FastAPI port
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
