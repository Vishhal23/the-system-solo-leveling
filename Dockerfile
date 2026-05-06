FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is sent straight to logs (no buffering)
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Initialize the database on build so it's ready at startup
RUN python -c "from db.database import init_database; init_database()"

# Expose Streamlit port (Render injects $PORT at runtime)
EXPOSE 8501

# Default: run the Telegram bot (overridden by render.yaml for dashboard)
CMD ["python", "run_bot.py"]
