#!/bin/bash
# Launch Simplex Outreach Dashboard
cd "$(dirname "$0")"
echo "🚀 Starting Simplex Outreach Dashboard..."
echo "   Open http://localhost:8501 in your browser"
echo ""
python3 -m streamlit run dashboard/app.py --server.port 8501
