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

# Expose the port Streamlit uses
EXPOSE 8501

# Copy and make the startup script executable
COPY start.sh .
RUN chmod +x start.sh

# Run the startup script
CMD ["./start.sh"]
