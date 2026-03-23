FROM python:3.12-slim

# Node.js 18+ required by Claude Agent SDK (bundles Claude Code CLI as subprocess)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash agent
WORKDIR /app

# Install Python dependencies
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Shared library on Python path
ENV PYTHONPATH=/app/lib/shared/src:$PYTHONPATH

# Railway assigns PORT dynamically
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

USER agent
CMD ["python", "server/server.py"]
