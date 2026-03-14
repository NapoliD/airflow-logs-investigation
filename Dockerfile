# Airflow Logs Investigation Toolkit
# Supports both basic demo and AI agents

FROM python:3.11-slim

LABEL maintainer="napolidata.com"
LABEL description="AI-powered Airflow log investigation toolkit"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY scripts/requirements.txt /app/scripts/
COPY ai_agents/requirements.txt /app/ai_agents/

# Install Python dependencies
RUN pip install --no-cache-dir -r scripts/requirements.txt \
    && pip install --no-cache-dir -r ai_agents/requirements.txt

# Copy the rest of the application
COPY . /app/

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command: run the AI agents demo in interactive mode
CMD ["python", "-m", "ai_agents.demo", "--mode", "interactive"]
