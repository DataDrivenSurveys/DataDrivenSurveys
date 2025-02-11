# This script modifies the Dockerfile and the compose.dev.yml file to add the platform: linux/amd64 to the frontend, backend and mariadb services
# It is made to ensure compatibility with ARM architecture, as the frontend and backend services are built originally for intel architecture
# author: @amroabdrabo

import platform


def add_platform_docker_compose(file_path):
    # Check if we're on ARM64 architecture
    is_arm64 = platform.machine().lower() in ['arm64', 'aarch64']

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    frontend=False # This variable being False means we have not yet appended platform: linux/amd64 after the frontend tag in the compose.dev.yml file
    backend = False
    db = False
    if is_arm64:
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
    else:
        # For non-ARM64: remove all platform: linux/amd64 lines
        lines = [line for line in lines if "platform: linux/amd64" not in line]
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == "__main__":
    add_platform_docker_compose("./compose.dev.yml")
    print("Successfully finished all modifications to compose.dev.yml")
