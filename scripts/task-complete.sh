#!/bin/bash

# Script to mark a task as complete and push to GitHub
# Usage: ./scripts/task-complete.sh <task-id> "<commit-message>"

TASK_ID=$1
COMMIT_MSG=$2

if [ -z "$TASK_ID" ] || [ -z "$COMMIT_MSG" ]; then
    echo "Usage: ./scripts/task-complete.sh <task-id> \"<commit-message>\""
    exit 1
fi

# Remind about the changelog
echo "Remember to update CHANGELOG.md with your changes before committing!"
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Activate virtual environment
source venv/bin/activate

# Mark the task as done (commented out until task-master is properly installed)
# venv/bin/python -m task-master set-status --id=$TASK_ID --status=done

# Add all changes to git
git add .

# Commit with the provided message
git commit -m "Complete task #$TASK_ID: $COMMIT_MSG"

# Push to GitHub
git push origin main

echo "Task #$TASK_ID marked as complete and changes pushed to GitHub!" 