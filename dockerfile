# Use Python slim image
FROM python:3.11-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching) 
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port for Railway
EXPOSE 8080

# Run the app with gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "server.app:app"]
