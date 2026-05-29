# --- Stage 1: Frontend Build ---
FROM node:22-slim as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Stage 2: Production ---
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Copy build artifacts to backend static directory
COPY --from=frontend-build /frontend/dist /app/static

# Expose Render default port
EXPOSE 10000
ENV PORT=10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
