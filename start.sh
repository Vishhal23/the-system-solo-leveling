#!/bin/bash

echo "Starting The System Telegram Bot..."
python run_bot.py &

echo "Starting The System Dashboard..."
streamlit run ui/dashboard.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
