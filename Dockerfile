FROM python:3.11-slim

# --- Python defaults ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- OS packages (gettext gives you msguniq, msgfmt, etc.) ---
RUN apt-get update \
 && apt-get install -y --no-install-recommends gettext \
 && rm -rf /var/lib/apt/lists/*

# --- Python deps ---
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# (optional) keep your env handy in dev
COPY .env.dev .env

# Copy the rest of the app only if you run the app from the image.
# If you're mounting the code via volumes in docker-compose, you can skip this.
# COPY . .
