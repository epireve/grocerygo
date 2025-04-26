# GroceryGo Development Scripts

This directory contains helpful scripts for developing the GroceryGo application.

## Development Workflow

### Starting the Development Environment

Run the development environment (Django + Tailwind CSS) with one command:

```bash
./scripts/run-dev.sh
```

This will:
1. Start the Tailwind CSS watcher
2. Start the Django development server on port 8000
3. Allow you to stop both with a single Ctrl+C

### Options

- **Custom port**: `./scripts/run-dev.sh 8001` - Run Django on port 8001
- **Apply migrations**: `./scripts/run-dev.sh --migrate` - Apply migrations before starting
- **Stop servers**: `./scripts/run-dev.sh stop` - Stop all running servers

### Task Completion

When you complete a task, use:

```bash
./scripts/task-complete.sh <task-id> "Description of what was done"
```

For example:
```bash
./scripts/task-complete.sh 5 "Implemented Tailwind CSS setup"
```

This will:
1. Mark the task as "done" in your task management system
2. Add all changes to Git
3. Create a commit with a descriptive message
4. Push to your GitHub repository

## Troubleshooting

If you're having issues with the development scripts:

1. Make sure both scripts are executable (`chmod +x scripts/*.sh`)
2. Check if there are any orphaned processes from previous runs
3. Make sure your virtual environment is properly set up 