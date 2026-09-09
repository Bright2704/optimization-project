#!/bin/bash
# ===========================================
#   Start Optimization Web Demo
#   วิธีใช้: ./start.sh หรือ bash start.sh
# ===========================================

echo "=================================================="
echo "  Starting Optimization Algorithms Web Demo..."
echo "  Open browser: http://localhost:8080"
echo "=================================================="
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Flask app
python3 app.py
