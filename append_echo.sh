#!/bin/bash

DOCKERFILE="Dockerfile"

# Check if the Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    echo "Error: $DOCKERFILE not found!"
    exit 1
fi

# Append the echo command to the Dockerfile
echo 'RUN echo "Build completed!"' >> "$DOCKERFILE"

echo "Echo command appended to $DOCKERFILE"
