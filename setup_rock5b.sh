#!/bin/bash
set -e

# 1. Update and upgrade
sudo apt update && sudo apt upgrade -y

# 2. Install required packages
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    lsb-release \
    gnupg \
    python3-pip \
    python3-venv

# 3. Install Docker (ARM64)
curl -fsSL https://get.docker.com | sudo sh

# 4. Add user to docker group
sudo usermod -aG docker $USER

# 5. Install Docker Compose v2 (as plugin, system-wide)
ARCH=arm64
VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f4)
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-linux-${ARCH} -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 6. Print Docker and Compose versions
docker --version
docker compose version

echo "Setup complete! Please log out and log back in to activate docker group permissions."
echo "You can now run Docker and Docker Compose commands without sudo." 