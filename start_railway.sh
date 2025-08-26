#!/bin/bash
# Railway start script for Streamlit app

# Set environment variables
export PYTHONPATH="/app/src:$PYTHONPATH"

# Start Streamlit app
streamlit run src/dashboard/crypto_app_unified.py \
  --server.port=${PORT:-8080} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --browser.gatherUsageStats=false
