# --- Frontend Build Stage ---
FROM node:22-slim as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Backend & Final Production Stage ---
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy frontend build artifacts to backend's static directory
COPY --from=frontend-build /frontend/dist /app/static

EXPOSE 10000

ENV PORT=10000

# Using sh -c to ensure environment variables like PORT are expanded if necessary,
# though uvicorn handles it well. Explicitly setting port 10000 for Render.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
