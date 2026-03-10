#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./draft.sh <your_file.md>"
  exit 1
fi

# Gets the absolute path so you can pass files from other directories
FILE_PATH=$(realpath "$1")
FILE_NAME=$(basename "$1")

docker run --rm \
  -v "$(pwd)":/app \
  -v "$(pwd)":/out \
  -w /app \
  mcr.microsoft.com/playwright/python:v1.58.0-jammy \
  bash -c "pip install -r requirements.txt -q && python draft.py $FILE_NAME"
