# Frontend Stage
FROM node:22.12.0-alpine3.21 AS frontend

# Change Working Directory To Client
WORKDIR /app/client

# Copy Package Files
COPY client/package*.json ./

# Install Dependencies
RUN npm install

# Copy Source Files
COPY client/ ./

# Copy ENV
COPY server/.env ./.env

# Build Application
RUN npm run build

# Backend Stage
FROM python:3.12-slim

# Change Working Directory To Root
WORKDIR /app

# Copy Requirements File
COPY server/pyproject.toml ./server/

# Install UV
RUN pip install --no-cache-dir uv

# Create Virtual Environment
RUN uv venv /app/venv

# Add Venv To Path
ENV PATH="/app/venv/bin:$PATH"

# Install Dependencies
RUN cd server && uv pip install .

# Copy Source Files
COPY server/ ./server/

# Copy Frontend Build
COPY --from=frontend /app/client/dist ./client/dist

# Expose Port 8080
EXPOSE 8080

# Change Working Directory To Server
WORKDIR /app/server

# Run Application
CMD ["python", "app.py"]