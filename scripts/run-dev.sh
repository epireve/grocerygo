#!/bin/bash

# Script to start the GroceryGo development environment
# This script starts both the Tailwind CSS watcher and Django server

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill running processes
cleanup() {
    echo -e "${YELLOW}Stopping servers...${NC}"
    
    # Kill tailwind process (save PID to file)
    if [ -f ".tailwind.pid" ]; then
        echo -e "${YELLOW}Stopping Tailwind CSS watcher...${NC}"
        TAILWIND_PID=$(cat .tailwind.pid)
        kill -9 $TAILWIND_PID 2>/dev/null
        rm .tailwind.pid
    fi
    
    # Kill Django process (save PID to file)
    if [ -f ".django.pid" ]; then
        echo -e "${YELLOW}Stopping Django server...${NC}"
        DJANGO_PID=$(cat .django.pid)
        kill -9 $DJANGO_PID 2>/dev/null
        rm .django.pid
    fi
    
    echo -e "${GREEN}All servers stopped successfully!${NC}"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Check if we're stopping the servers
if [ "$1" == "stop" ]; then
    cleanup
    exit 0
fi

# Check for --migrate flag
MIGRATE=false
if [ "$1" == "--migrate" ] || [ "$2" == "--migrate" ]; then
    MIGRATE=true
fi

# Activate virtual environment
source venv/bin/activate

# Apply migrations if requested
if [ "$MIGRATE" = true ]; then
    echo -e "${BLUE}Applying database migrations...${NC}"
    venv/bin/python manage.py migrate
fi

# Start the Tailwind CSS watcher in background
echo -e "${BLUE}Starting Tailwind CSS watcher...${NC}"
venv/bin/python manage.py tailwind start &
TAILWIND_PID=$!
echo $TAILWIND_PID > .tailwind.pid
echo -e "${GREEN}Tailwind CSS watcher started (PID: $TAILWIND_PID)${NC}"

# Small delay to let Tailwind start properly
sleep 2

# Start the Django server (port 8000 by default)
DJANGO_PORT=${1:-8000}
if [ "$1" == "--migrate" ]; then
    DJANGO_PORT=8000
fi

echo -e "${BLUE}Starting Django server on port $DJANGO_PORT...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
venv/bin/python manage.py runserver $DJANGO_PORT &
DJANGO_PID=$!
echo $DJANGO_PID > .django.pid

# Keep script running to manage processes
echo -e "${GREEN}Development environment running!${NC}"
echo -e "${GREEN}Django server:         http://127.0.0.1:$DJANGO_PORT/${NC}"
echo -e "${BLUE}--------------------------------------------${NC}"
echo -e "${YELLOW}Commands:${NC}"
echo -e "  ${GREEN}- ./scripts/run-dev.sh stop${NC}      # Stop all servers"
echo -e "  ${GREEN}- ./scripts/run-dev.sh <port>${NC}    # Run with custom Django port"
echo -e "  ${GREEN}- ./scripts/run-dev.sh --migrate${NC} # Apply migrations before starting"

# Wait for processes to finish (or Ctrl+C)
wait 