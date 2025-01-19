# Makefile for automating tasks

# Variables
PROJECT = NeuroReact
TARGET ?= src/rectangle.py
TARGET_TEST ?= src/rectangle.py
MAIN_BRANCH ?= main

# IP address of Raspberry PI (only static support)
REMOTE_PI_IP = 192.168.1.137

# Remote user and pwd paths
REMOTE_PI_USER = amosor
REMOTE_PI_PWD = data/$(PROJECT)/$(PROJECT)

# Sync with repository
.PHONY: update, run, all, run_remote, end_remote
update:
	@git pull origin $(MAIN_BRANCH)

# Run the main Python script - on remote ONLY
run:
	@python3 $(TARGET_TEST)

# Run outside of the remote
# Allow forcefully usage of interactive session when running remotely 
run_remote:
	ssh -t $(REMOTE_PI_USER)@$(REMOTE_PI_IP) 'cd $(REMOTE_PI_PWD) && make all'

# Update and run
all: update run_remote

