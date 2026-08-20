# Build context is the REPO ROOT (not backend/), so this image can also
# bundle testbed/ as scannable sample repos. See docker-compose.yml and the
# Render deploy notes for how the context/dockerfile path are wired up.

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY testbed/ ./testbed/

# Render provides $PORT; default to 8000 for local/docker-compose use.
# EXPOSE tells Render (and docker-compose) which port to route to for a
# Docker-runtime service — without it, platforms can't infer the port.
ENV PORT=8000
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
