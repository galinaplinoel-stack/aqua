#!/bin/bash
# AQUA Quick Start Script

set -e

echo "🚀 AQUA Quick Start"
echo "==================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run setup wizard:    python3 main.py --setup"
echo "  2. Or quick setup:      python3 main.py --quick-setup YOUR_API_KEY openai"
echo "  3. Then run:            python3 main.py"
echo ""
echo "Providers: openai, openrouter, together, groq, mimo"
echo ""
