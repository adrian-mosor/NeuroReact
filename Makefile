# Makefile for automating tasks

# Variables
PROJECT = NeuroReact
TARGET ?= src/main.py
TARGET_TEST ?= src/test/rectangle.py
MAIN_BRANCH ?= develop

# IP address of Raspberry PI (only static support)
REMOTE_PI_IP = 192.168.1.137

# Remote user and pwd paths
REMOTE_PI_USER = amosor
REMOTE_PI_PWD = /home/amosor/data/$(PROJECT)/$(PROJECT)

# Sync with repository
.PHONY: update, run, all, run_remote
update:
	@git pull
	@git checkout $(MAIN_BRANCH)

# Run the main Python script - on remote ONLY
run:
	@python3 $(TARGET_TEST)

# Run outside of the remote
# Allow forcefully usage of interactive session when running remotely 
run_remote:
	ssh -t $(REMOTE_PI_USER)@$(REMOTE_PI_IP) 'cd $(REMOTE_PI_PWD) && make update && make run'

# Update and run
all: update run_remote

