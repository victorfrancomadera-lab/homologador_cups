# ---------- Etapa 1: compilar el frontend React ----------
FROM node:20-alpine AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---------- Etapa 2: backend FastAPI + frontend compilado ----------
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Dependencias del backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Codigo del backend y datos semilla
COPY backend/app ./app
COPY backend/seed_data ./seed_data

# Frontend compilado desde la etapa anterior
COPY --from=frontend /fe/dist ./frontend_dist

# Railway inyecta $PORT
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
