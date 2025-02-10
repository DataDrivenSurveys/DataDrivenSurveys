# This script modifies the Dockerfile and the compose.dev.yml file to add the platform: linux/amd64 to the frontend, backend and mariadb services
# It is made to ensure compatibility with ARM architecture, as the frontend and backend services are built originally for intel architecture
# author: @amroabdrabo

import platform

def modify_first_from_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    token = "FROM --platform=linux/amd64 " # modify the first line so that we guarantee the image is built for linux/amd64
    modified = False
    for i, line in enumerate(lines):
        if "linux/amd64" in line:
            break
        if line.startswith("FROM") and not modified:
            lines[i] = token + line[5:]
            modified = True
            break
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def add_platform_docker_compose(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    frontend=False # This variable being False means we have not yet appended platform: linux/amd64 after the frontend tag in the compose.dev.yml file
    backend = False
    db = False

    for i, line in enumerate(lines):
        if "frontend" in line:
            if "linux/amd64" in lines[i+1]: # Never insert the platform: linux/amd64 twice
                frontend = True
            if not frontend:
                lines.insert(i + 1, "    platform: linux/amd64\n")
                frontend = True
        if "backend" in line:
            if "linux/amd64" in lines[i+1]:
                backend = True
            if not backend:
                lines.insert(i + 1, "    platform: linux/amd64\n")
                backend = True
        if "mariadb" in line:
            if "linux/amd64" in lines[i-1] or "linux/amd64" in lines[i]:
                db = True
            if not db:
                lines.insert(i, "    platform: linux/amd64\n")
                db = True
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def is_arm_architecture():
    arch = platform.machine().lower()
    return arch in ["arm64", "aarch64"]

if __name__ == "__main__":
    if is_arm_architecture(): # only run the code if the architecture is ARM
        modify_first_from_line("./Dockerfile")
        add_platform_docker_compose("./compose.dev.yml")
        print("Successfully finished all modifications to Dockerfile and compose.dev.yml")
