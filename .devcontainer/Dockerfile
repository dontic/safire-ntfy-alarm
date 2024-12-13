# Dockerfile

# Get the base image
FROM python:3.11-bullseye

# Apt update
RUN apt update

# Install git
RUN apt install -y git

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1