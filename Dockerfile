# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 7000

# Run migrations and create superuser, then start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py import_data && python manage.py collectstatic --noinput && python create_superuser.py && python manage.py runserver 0.0.0.0:7001"]



