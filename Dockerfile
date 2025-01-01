# Base image: Use the latest Python 3.12-slim as foundation
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED 1         # Disable buffering for better log visibility
ENV FLASK_APP flask_app/app.py
ENV FLASK_CONFIG production

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first for dependency installation
COPY requirements/docker.txt requirements.txt

# Install system dependencies and Python requirements
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire application code into the container
COPY flask_app /app/flask_app
COPY boot.sh config.py gunicorn.conf.py /app/

# Ensure that boot.sh is executable
RUN chmod +x /app/boot.sh

# Create a dedicated user and fix directory permissions
RUN useradd -m flaskuser && \
    chown -R flaskuser:flaskuser /app

# Switch to the non-root user for security
USER flaskuser

# Expose the application port (8000) for Gunicorn
EXPOSE 8000

# Use boot.sh as the default entry point
CMD ["/app/boot.sh"]