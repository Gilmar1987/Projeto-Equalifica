# syntax=docker/dockerfile:1
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=equalifica_project.settings

WORKDIR /app

# Instalar dependências do sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copiar código
COPY . /app

EXPOSE 8000

# Comando padrão (executado/override pelo docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]