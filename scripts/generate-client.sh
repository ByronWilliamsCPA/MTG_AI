#!/usr/bin/env bash
# Generate TypeScript API client from FastAPI OpenAPI schema
# Usage: ./scripts/generate-client.sh [api_url]

set -euo pipefail

# Configuration
API_URL="${1:-http://localhost:8000}"
FRONTEND_DIR="$(dirname "$0")/../frontend"
OUTPUT_DIR="$FRONTEND_DIR/src/client"

echo "🔄 Generating TypeScript API client..."
echo "   API URL: $API_URL"
echo "   Output:  $OUTPUT_DIR"

# Check if backend is running
if ! curl -s "$API_URL/openapi.json" > /dev/null 2>&1; then
    echo "" >&2
    echo "❌ Error: Cannot reach API at $API_URL" >&2
    echo "" >&2
    echo "Make sure the backend is running:" >&2
    echo "  cd $(dirname "$0")/.." >&2
    echo "  uv run uvicorn mtg_ai.main:app --reload" >&2
    echo "" >&2
    exit 1
fi

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Generate client
echo ""
echo "📝 Generating client from OpenAPI schema..."
npm run generate-client

echo ""
echo "✅ API client generated successfully!"
echo ""
echo "Usage in your React components:"
echo ""
echo "  import { client } from '@/client'"
echo "  const response = await client.get('/api/endpoint')"
echo ""
