#!/bin/bash

# migrations.sh - Helper script for managing database migrations in GroceryGo
# Usage: ./scripts/migrations.sh [command] [app_name] [migration_name]

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate virtual environment
source venv/bin/activate

# Check for required arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: Missing command argument${NC}"
    echo -e "${YELLOW}Usage: ./scripts/migrations.sh [command] [app_name] [migration_name]${NC}"
    echo -e "${BLUE}Commands:${NC}"
    echo -e "  ${GREEN}apply${NC}           Apply all pending migrations"
    echo -e "  ${GREEN}make [app]${NC}      Create migrations (for all or specific app)"
    echo -e "  ${GREEN}status${NC}          Show migration status"
    echo -e "  ${GREEN}revert app ver${NC}  Revert app to specific migration version"
    exit 1
fi

COMMAND=$1
APP_NAME=$2
MIGRATION_NAME=$3

case $COMMAND in
    "apply")
        echo -e "${BLUE}Applying all pending migrations...${NC}"
        venv/bin/python manage.py migrate
        ;;
    "make")
        if [ -z "$APP_NAME" ]; then
            echo -e "${BLUE}Creating migrations for all apps...${NC}"
            venv/bin/python manage.py makemigrations
        else
            echo -e "${BLUE}Creating migrations for $APP_NAME...${NC}"
            venv/bin/python manage.py makemigrations $APP_NAME
        fi
        ;;
    "status")
        echo -e "${BLUE}Showing migration status...${NC}"
        venv/bin/python manage.py showmigrations
        ;;
    "revert")
        if [ -z "$APP_NAME" ] || [ -z "$MIGRATION_NAME" ]; then
            echo -e "${RED}Error: Missing app_name or migration_name${NC}"
            echo -e "${YELLOW}Usage: ./scripts/migrations.sh revert app_name migration_name${NC}"
            exit 1
        fi
        echo -e "${BLUE}Reverting $APP_NAME to migration $MIGRATION_NAME...${NC}"
        venv/bin/python manage.py migrate $APP_NAME $MIGRATION_NAME
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo -e "${YELLOW}Available commands: apply, make, status, revert${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}Migration command completed successfully!${NC}" 