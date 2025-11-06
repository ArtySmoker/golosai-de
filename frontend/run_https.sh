#!/bin/bash
streamlit run main.py \
  --server.port=3000 \
  --server.address=0.0.0.0 \
  --server.enableCORS=true \
  --server.enableXsrfProtection=false