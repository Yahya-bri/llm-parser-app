FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

# Set working directory
WORKDIR /app

# Install system dependencies required for PyMuPDF and pdf2image
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    poppler-utils \
    # Dependencies for PyMuPDF
    libmupdf-dev \
    swig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Copy entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' django

# Create directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/media/documents
RUN chown -R django:django /app
RUN chmod -R 755 /app/staticfiles /app/media

# Make sure the media directories have write permissions
RUN chmod -R 777 /app/media

USER django

# Expose portput\n\necho "Starting Gunicorn..."\nexec gunicorn --bind 0.0.0.0:8000 config.wsgi' > /app/entrypoint.sh
EXPOSE 8000

# Create a startup script with proper migration handling
RUN echo '#!/bin/sh\nset -e\npython manage.py makemigrations\npython manage.py migrate\npython manage.py collectstatic --noinput\necho "Starting Gunicorn..."\nexec gunicorn --bind 0.0.0.0:8000 config.wsgi' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/docker-entrypoint.sh"]
