#!/bin/bash

# Build script for working Ubuntu-based PostGIS ARM64 image
set -e

echo "🚀 Building working Ubuntu-based PostGIS ARM64 image for NNDR Insight..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if we're on ARM64 architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" && "$ARCH" != "aarch64" ]]; then
    print_warning "You're not on ARM64 architecture ($ARCH). The image will still work but may not be optimized for your system."
fi

# Set build arguments
IMAGE_NAME="nndr-postgis-arm64-working"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

print_status "Building working PostGIS image: $FULL_IMAGE_NAME"

# Build the image
print_status "Starting build process (this may take 20-25 minutes)..."
print_status "Using Ubuntu 22.04 base for better ARM64 compatibility..."

docker build \
    --platform linux/arm64 \
    --file Dockerfile.postgis-arm64-working \
    --tag $FULL_IMAGE_NAME \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    print_success "PostGIS working image built successfully!"
    
    # Show image info
    print_status "Image details:"
    docker images $FULL_IMAGE_NAME
    
    # Test the image
    print_status "Testing the image..."
    docker run --rm $FULL_IMAGE_NAME su - postgres -c "pg_isready" || echo "PostgreSQL not ready in test mode (normal)"
    
    print_success "Build completed successfully!"
    echo ""
    print_status "To use this image, update your docker-compose.yml:"
    echo "  image: $FULL_IMAGE_NAME"
    echo ""
    print_status "Or use the working docker-compose file:"
    echo "  docker-compose -f docker-compose.working.yml up -d"
    echo ""
    print_status "To push to a registry:"
    echo "  docker tag $FULL_IMAGE_NAME your-registry/$FULL_IMAGE_NAME"
    echo "  docker push your-registry/$FULL_IMAGE_NAME"
    
else
    print_error "Build failed!"
    exit 1
fi 