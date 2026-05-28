# --- Backend Build Stage ---
FROM python:3.11-slim as backend

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# --- Frontend Build Stage ---
FROM node:22-slim as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Final Production Stage ---
FROM python:3.11-slim
WORKDIR /app
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin
COPY --from=backend /app /app
COPY --from=frontend-build /frontend/dist /app/static

# Note: In production, we'd serve the static files via FastAPI or Nginx
# For this setup, we'll assume FastAPI serves them or it's a separate container.
# Let's adjust main.py to serve static files if they exist.

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
