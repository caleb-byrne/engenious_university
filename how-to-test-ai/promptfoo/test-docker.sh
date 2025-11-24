#!/bin/bash
set -e

echo "🔍 Testing Promptfoo Docker Setup..."

# Check if we're in the right directory
if [ ! -f "Red-Teaming/Dockerfile.redteam" ]; then
    echo "❌ Please run this script from the promptfoo directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env file exists in Red-Teaming directory
if [ ! -f "Red-Teaming/.env" ]; then
    echo "⚠️  No .env file found in Red-Teaming directory"
    echo "Please create Red-Teaming/.env with:"
    echo "OPENAI_API_KEY=your_api_key_here"
    
    # Create a sample .env file
    echo "Creating sample .env file..."
    cat > Red-Teaming/.env << EOF
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo "📝 Sample .env file created at Red-Teaming/.env"
    echo "Please edit it with your actual API key before running tests"
    exit 1
fi

# Load environment variables
source Red-Teaming/.env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Please set OPENAI_API_KEY in Red-Teaming/.env file"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create output directory
mkdir -p Red-Teaming/output

echo "🏗️  Building Docker image..."
docker build -f Red-Teaming/Dockerfile.redteam -t promptfoo-redteam:test ./Red-Teaming

echo "✅ Image built successfully"

echo "🔍 Testing promptfoo version..."
docker run --rm promptfoo-redteam:test npx promptfoo --version

echo "🧪 Running red-team tests..."
docker run --rm \
    --env-file Red-Teaming/.env \
    -v "$(pwd)/Red-Teaming/output:/app/output" \
    promptfoo-redteam:test

echo "📊 Checking for output files..."
if ls Red-Teaming/output/*.json >/dev/null 2>&1; then
    echo "✅ Output files generated successfully:"
    ls -la Red-Teaming/output/
else
    echo "⚠️  No JSON output files found"
fi

echo ""
echo "🎉 Docker setup test completed!"
echo "📂 Results are in Red-Teaming/output/"
echo ""
echo "Next steps:"
echo "1. Review the results in Red-Teaming/output/"
echo "2. Test with docker-compose: docker-compose up"
echo "3. Add this setup to your CI/CD pipeline"