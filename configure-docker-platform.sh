#!/bin/bash

# Detect system architecture
ARCH=$(uname -m)

# Set default platform based on architecture
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    echo "Detected ARM64 architecture"
    
    # Update Dockerfile
    if [ -f "Dockerfile" ]; then
        awk '
            /^FROM/ && !/#/ {  # Only match uncommented FROM lines
                if (!match($0, "--platform")) {
                    sub(/^FROM /, "FROM --platform=linux/amd64 ")
                }
            }
            { print }
        ' Dockerfile > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile
    fi
    
    # Update compose.dev.yml specifically for the backend service
    if [ -f "compose.dev.yml" ]; then
        awk '
            { print }
            /^[[:space:]]*backend:/ {   # Matches "backend:" even if preceded by spaces/tabs
                print "    platform: linux/amd64"
            }
            /^[[:space:]]*frontend:/ {   # Matches "backend:" even if preceded by spaces/tabs
                print "    platform: linux/amd64"
            }
            /^[[:space:]]*db:/ {   # Matches "backend:" even if preceded by spaces/tabs
                print "    platform: linux/amd64"
            }
        ' compose.dev.yml > compose.dev.yml.tmp && mv compose.dev.yml.tmp compose.dev.yml
    fi
    
    echo "Updated Docker configuration files for AMD64 platform"
else
    echo "Detected x86_64 architecture"
    
    # Update Dockerfile
    if [ -f "Dockerfile" ]; then
        awk '
            /^FROM/ && !/#/ {  # Only match uncommented FROM lines
                sub(/--platform=linux\/amd64 /, "")
            }
            { print }
        ' Dockerfile > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile
    fi
    
    # Remove platform from compose.dev.yml
    if [ -f "compose.dev.yml" ]; then
        awk '!/^  platform: linux\/amd64/' compose.dev.yml > compose.dev.yml.tmp && mv compose.dev.yml.tmp compose.dev.yml
    fi
    
    echo "Removed platform specifications from Docker configuration files"
fi

echo "Docker configuration update complete"