# Backend Stage
FROM python:3.12-slim

# Change Working Directory To Root
WORKDIR /app

# Copy Requirements File
COPY server/pyproject.toml ./

# Install UV
RUN pip install --no-cache-dir uv

# Create Virtual Environment
RUN uv sync

# Copy Source Files
COPY server/ ./

# Expose Port 3000
EXPOSE 3000

# Change Working Directory To Server
WORKDIR /app

# Run Application
CMD ["uv", "run", "app.py"]