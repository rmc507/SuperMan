# SuperMan CLI Tool

SuperMan is a Python-based CLI tool that uses a local LLM (via Ollama) to assist with system administration tasks and bash command understanding. It provides various modes of operation to help users better understand and work with Linux commands, including a command execution feature.

## Features

- Command explanations and historical context
- Command summarization (brief and detailed)
- Command cheatsheet generation
- System administration assistance
- Command troubleshooting with history analysis
- Command discovery
- Task planning assistance
- Safe command execution based on natural language descriptions

## Prerequisites

- Python 3.7+
- Ollama installed and running (https://ollama.ai)
- Default LLM model: qwen2.5:14b-instruct-q4_1

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rmc507/superman.git
cd superman
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the CLI tool:
```bash
# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Copy the superman bash script to your bin directory
cp superman ~/bin/
chmod +x ~/bin/superman

# Add the following line to your .bashrc
echo "alias superman='history | tail -50 > /tmp/superman_current_history && ~/bin/superman'" >> ~/.bashrc

# Reload your .bashrc
source ~/.bashrc
```

## Docker Installation

Alternative to local installation, you can run SuperMan in Docker:

1. Make the script executable:
```bash
chmod +x run-superman.sh
```

2. Run with arguments:
```bash
./run-superman.sh -a "How do I check disk space?"
```

Or run interactively:
```bash
./run-superman.sh
```

## Usage Examples

1. Get command information:
```bash
superman ls
```

2. Get a brief summary:
```bash
superman wget --shortsum
```

3. Generate a command cheatsheet:
```bash
superman tar -c
```

4. Get system administration help:
```bash
superman -a "How do I find large files on my system?"
```

5. Analyze recent commands:
```bash
superman -t 5
```

6. Execute a command based on description:
```bash
superman -e "show current directory contents in a detailed format"
```

## Available Options

- `-s, --summarize`: Detailed command summary
- `--shortsum`: One-line command summary
- `-c, --cheat`: Generate command cheatsheet
- `-a, --assistant`: General system administration help
- `-f, --find`: Discover commands for specific tasks
- `-t, --trouble [N]`: Analyze last N commands (default: 10)
- `-p, --plan`: Create task execution plan
- `-e, --exec`: Execute command based on description

## Safety Features

The command execution mode includes:
- Comprehensive command blacklist
- Pattern-based security checks
- Confirmation system for potentially dangerous commands
- Real-time command output streaming

## Configuration

The default model is set to `qwen2.5:14b-instruct-q4_1`. To use a different model, modify the `model_name` parameter in `superman.py`:

```python
def __init__(self, model_name='your-preferred-model', mode='default'):
```

## Limitations

- Requires Ollama to be running
- Response quality depends on the LLM model used
- May have longer response times with larger models
- Some system commands are restricted for safety

## License

This project is licensed under the MIT License - see the LICENSE file for details.
