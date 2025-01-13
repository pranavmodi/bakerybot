#!/bin/bash

# Check if commit message is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a commit message"
    echo "Usage: $0 \"your commit message\""
    exit 1
fi

# Add all changes to staging
git add .

# Commit changes with provided message
git commit -m "$1"

# Push changes to main branch
git push origin main