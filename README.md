# Expense Tracker API + MCP

A FastAPI expense tracker that stores expenses in a local SQLite database, exposed as an MCP (Model Context Protocol) server so Claude Desktop can manage your expenses directly.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- [Claude Desktop](https://claude.ai/download)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Prannav-Bansal/FastAPI-MCP.git
cd FastAPI-MCP
```

### 2. Install dependencies

```bash
uv sync
```

This installs all dependencies defined in `pyproject.toml` into a local virtual environment:
- `fastapi`
- `fastmcp`
- `sqlalchemy`
- `uvicorn`

## Run the API

To run the FastAPI server directly:

```bash
uv run uvicorn main:app --reload
```

Open the API docs at:

```
http://127.0.0.1:8000/docs
```

## Connect to Claude Desktop (MCP)

### 1. Find your `uv` path

**Windows:**
```powershell
where uv
```

**macOS/Linux:**
```bash
which uv
```

### 2. Find your Claude Desktop config file

| OS | Path |
|----|------|
| Windows (Store) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` |
| Windows (Direct install) | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### 3. Add the MCP server to your config

Open the config file and add the `mcpServers` block. Replace the `command` path with your actual `uv` path from step 1, and update the directory path to where you cloned this repo.

**Windows example:**
```json
{
  "mcpServers": {
    "expensetracker": {
      "command": "C:\\path\\to\\uv.exe",
      "args": [
        "--directory",
        "C:\\path\\to\\FastAPI-MCP",
        "run",
        "server.py"
      ]
    }
  }
}
```

**macOS/Linux example:**
```json
{
  "mcpServers": {
    "expensetracker": {
      "command": "/usr/local/bin/uv",
      "args": [
        "--directory",
        "/path/to/FastAPI-MCP",
        "run",
        "server.py"
      ]
    }
  }
}
```

> **Important:** Use `--directory` instead of `cwd` so `uv` picks up the project's virtual environment where all dependencies are installed.

### 4. Restart Claude Desktop

Fully quit Claude Desktop from the system tray and reopen it. You should see a 🔨 hammer icon in the chat input — that confirms the MCP server is connected.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/expenses` | Add an expense |
| `GET` | `/expenses` | List all expenses |
| `GET` | `/expenses/summary` | Total count and amount |
| `GET` | `/expenses/{expense_id}` | Get one expense |
| `DELETE` | `/expenses/{expense_id}` | Delete one expense |

## Example Expense

```json
{
  "title": "Lunch",
  "amount": "250.00",
  "category": "Food",
  "spent_on": "2026-05-27",
  "note": "Office lunch"
}
```

## Project Structure

```
FastAPI-MCP/
├── main.py          # FastAPI app with all endpoints
├── server.py        # FastMCP server (wraps the FastAPI app for Claude)
├── pyproject.toml   # Project dependencies
├── requirements.txt # pip-compatible requirements
└── uv.lock          # Locked dependency versions
```