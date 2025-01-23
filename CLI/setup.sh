#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No color

# Set the default repository URL
REPO_URL="https://github.com/ION-WorkoutApp/server.git"

# Function to generate random secrets and encode them
uri_encode() {
    local string="${1}"
    local encoded=""
    for (( i=0; i<${#string}; i++ )); do
        local char="${string:i:1}"
        case "$char" in
            [a-zA-Z0-9._~-]) # Safe characters
                encoded+="$char"
                ;;
            *) # Encode all other characters
                encoded+="$(printf '%%%02X' "'$char")"
                ;;
        esac
    done
    echo "$encoded"
}

generate_secret() {
    # Generates a mix of alphanumeric characters and special characters compatible with MongoDB
    tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=' < /dev/urandom | head -c "$1"
}

# Ask the user whether to generate credentials automatically
echo -e "${CYAN}Do you want to use randomly generated values for the MongoDB password and secret key? (yes/no) [default: yes]:${NC}"
read -p "> " AUTO_GENERATE
AUTO_GENERATE=${AUTO_GENERATE:-yes}

if [[ "$AUTO_GENERATE" =~ ^(yes|y|Y)$ ]]; then
    # Generate random credentials
    MONGO_PASSWORD=$(generate_secret 32)
    SECRET_KEY=$(generate_secret 32)
    echo -e "${YELLOW}Generated credentials:${NC}"
    echo -e "${GREEN}MongoDB Password:${NC} $MONGO_PASSWORD"
    echo -e "${GREEN}Secret Key:${NC} $SECRET_KEY"
else
    # Prompt the user for manual input
    echo -e "${CYAN}Enter the MongoDB Password:${NC}"
    read -p "> " MONGO_PASSWORD
    if [[ -z "$MONGO_PASSWORD" ]]; then
        echo -e "${RED}Error: MongoDB Password cannot be empty.${NC}"
        exit 1
    fi

    echo -e "${CYAN}Enter the Secret Key:${NC}"
    read -p "> " SECRET_KEY
    if [[ -z "$SECRET_KEY" ]]; then
        echo -e "${RED}Error: Secret Key cannot be empty.${NC}"
        exit 1
    fi
fi

# Prompt the user for other inputs
echo -e "${CYAN}Enter the MongoDB Username [default: workoutadmin]:${NC}"
read -p "> " MONGO_USER
MONGO_USER=${MONGO_USER:-workoutadmin}

echo -e "${CYAN}Enter the PORT [default: 1221]:${NC}"
read -p "> " PORT
PORT=${PORT:-1221}

echo -e "${CYAN}Enter the MongoDB Database [default: maindb]:${NC}"
read -p "> " MONGO_DATABASE
MONGO_DATABASE=${MONGO_DATABASE:-maindb}

echo -e "${CYAN}Enable debugging? (true/false) [default: true]:${NC}"
read -p "> " DEBUGGING
DEBUGGING=${DEBUGGING:-true}

# Clone the repository
echo -e "${BLUE}Cloning the repository...${NC}"
if git clone "$REPO_URL"; then
    REPO_NAME=$(basename "$REPO_URL" .git)
    echo -e "${GREEN}Repository cloned into $REPO_NAME.${NC}"
    cd "$REPO_NAME" || { echo -e "${RED}Error: Failed to enter directory $REPO_NAME.${NC}"; exit 1; }
else
    echo -e "${RED}Error: Failed to clone the repository.${NC}"
    exit 1
fi

# Write the .env file
ENV_PATH="$(pwd)/.env"
echo -e "${BLUE}Creating .env file at $ENV_PATH...${NC}"
{
    echo "PORT=$PORT"
    echo "SECRET_KEY=$SECRET_KEY"
    echo "MONGO_URI=mongodb://$MONGO_USER:$(uri_encode "$MONGO_PASSWORD")@mongodb:27017/$MONGO_DATABASE?authSource=admin"
    echo "MONGO_INITDB_ROOT_USERNAME=$MONGO_USER"
    echo "MONGO_INITDB_ROOT_PASSWORD=$MONGO_PASSWORD"
    echo "MONGO_DATABASE=$MONGO_DATABASE"
    echo "DEBUGGING=$DEBUGGING"
} > "$ENV_PATH"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}.env file created successfully.${NC}"
else
    echo -e "${RED}Error: Failed to write the .env file.${NC}"
    exit 1
fi

# Pull Docker images
echo -e "${BLUE}Pulling Docker images...${NC}"
if docker compose pull; then
    echo -e "${GREEN}Docker images pulled successfully.${NC}"
else
    echo -e "${RED}Error: Failed to pull Docker images.${NC}"
    exit 1
fi

echo -e "${GREEN}Server setup completed!${NC}"
