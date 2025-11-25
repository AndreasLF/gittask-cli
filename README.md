# Git-Asana CLI & Time Tracker

A CLI tool that seamlessly integrates Git branching with Asana task management and time tracking.

## Features

- **Automatic Time Tracking**: Tracks time spent on branches.
- **Asana Integration**: Links branches to Asana tasks.
- **Sync**: Pushes time logs to Asana as comments.
- **Dashboard**: View your current work status.

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

### 1. Help Command
Verify that the CLI is installed and shows help.
```bash
gittask --help
```

### 2. Auth (Interactive)
Authenticate with your Asana Personal Access Token.
```bash
gittask auth login
```

### 3. Init (Interactive)
Select your default Workspace and Project.
```bash
gittask init
```

### 4. Checkout & Time Tracking
The core feature: switching branches automatically tracks time.

```bash
# Create a new branch and link it to an Asana task (interactive)
gittask checkout -b feature/test-branch

# Switch back to main (stops tracking the previous branch)
gittask checkout main
```

### 5. Status
View your current session and recent unsynced sessions.
```bash
gittask status
```

### 6. Sync
Push your time logs to Asana as comments.
```bash
gittask sync
```
