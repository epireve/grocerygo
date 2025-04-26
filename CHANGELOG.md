# Changelog

All notable changes to the GroceryGo project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-04-26

### Added

1. Project initialization
   - Created virtual environment and installed dependencies
   - Initialized Django project structure
   - Set up directory structure for templates, static files, and media

2. Django configuration
   - Configured Django settings
   - Set up static and media files configuration
   - Added core app to INSTALLED_APPS

3. Database setup
   - Configured SQLite database
   - Applied initial migrations
   - Created superuser for admin access

4. Tailwind CSS integration
   - Set up Tailwind CSS for styling
   - Configured Tailwind CSS to work with Django

5. URL configuration
   - Set up URL routing in core/urls.py
   - Updated project URLconf to include core app URLs
   - Added media and static file URL configurations

6. Basic templates
   - Created base.html template with Tailwind CSS
   - Created home.html template that extends base.html

7. Development tools
   - Created run-dev.sh script to start both Django and Tailwind CSS servers
   - Created task-complete.sh script for task completion and GitHub push
   - Added documentation for development workflow 