#!/bin/bash
# TZMICHA AI OS - Quick Setup Script

echo "================================"
echo "  TZMICHA AI OS - Setup"
echo "================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker found"

# Copy env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env (add your API keys)"
else
    echo "✓ .env exists"
fi

# Start infra
echo "Starting infrastructure..."
docker compose up -d postgres redis qdrant
echo "✓ PostgreSQL, Redis, Qdrant running"

# Install Python deps
echo "Installing Python dependencies..."
cd apps/api && pip install -r requirements.txt -q
cd ../..

echo ""
echo "================================"
echo "  ✅ Setup Complete!"
echo "  Run: make dev"
echo "================================"
