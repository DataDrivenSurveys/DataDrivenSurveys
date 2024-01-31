# Docker Setup

## Setting up Docker on Debian

If you are using the Debian GNU/Linux distribution, follow the instructions at the following link:

[https://docs.docker.com/desktop/install/debian/](https://docs.docker.com/desktop/install/debian/)

## Detailed Docker Setup Instructions

### Step 1 - Setup Docker's package repository 
https://docs.docker.com/engine/install/debian/#set-up-the-repository


Set up the repository
Update the apt package index and install packages to allow apt to use a repository over HTTPS:

```bash
 sudo apt-get update
 sudo apt-get install ca-certificates curl gnupg
```

Add Docker’s official GPG key:

```bash
 sudo install -m 0755 -d /etc/apt/keyrings
 curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
 sudo chmod a+r /etc/apt/keyrings/docker.gpg
Use the following command to set up the repository:
```

```bash
 echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## Step 2 - Download latest DEB package.
    
```bash
wget https://desktop.docker.com/linux/main/amd64/docker-desktop-4.19.0-amd64.deb?utm_source=docker&utm_medium=webreferral&utm_campaign=docs-driven-download-linux-amd64
```

rename the downloaded DEB package to docker-desktop-4.19.0-amd64.deb
```bash
mv docker-desktop-4.19.0-amd64.deb\?utm_source\=docker docker-desktop-4.19.0-amd64.deb
```

### Step 3 - Install Docker Desktop

```bash
sudo apt-get update
sudo apt-get install ./docker-desktop-4.19.0-amd64.deb
```

Step indicated there should be an error message by the end of the installation due to the fact we install the downloaded package. 

There are a few post-install configuration steps done through the post-install script contained in the deb package.

The post-install script:

Sets the capability on the Docker Desktop binary to map privileged ports and set resource limits.
Adds a DNS name for Kubernetes to /etc/hosts.
Creates a link from /usr/bin/docker to /usr/local/bin/com.docker.cli.

### Step 4 - Start Docker
```bash
systemctl --user start docker-desktop

```

### Step 5 - Verify Docker is running
```bash
docker compose version
# Docker Compose version v2.17.3

dopcker --version
# Docker version 23.0.6, build ef23cbc

docker version
# Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
# Client: Docker Engine - Community
# Cloud integration: v1.0.31
# Version:           23.0.6
# API version:       1.42
# Go version:        go1.19.9
# Git commit:        ef23cbc
# Built:             Fri May  5 21:18:28 2023
# OS/Arch:           linux/amd64
# Context:           default

docker run hello-world
```

### Step 6 - Post install - enable docker desktop to start on boot
```bash
systemctl --user enable docker-desktop
```


## Step 7 - Docker is not installed correctly on Debian
Based on the output of the `docker version` command, it seems that docker engine is not installed correctly on Debian.

It is unclear if, in the step 1, we need to proceed with the installation of the docker engine or not. Or should we just "Set up Docker’s package repository.".

Proceeding with the section [Install Docker Engine](https://docs.docker.com/engine/install/debian/#install-docker-engine) of the documentation.


```bash
 sudo apt-get update
 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```bash
sudo docker run hello-world
## Hello from Docker!
```

### Add "admin" user into the docker group

```bash
sudo usermod -aG docker admin
```
