# SuperMan CLI Tool

SuperMan is a Python-based CLI tool that uses a local LLM (via Ollama) to assist with system administration tasks and bash command understanding. It provides various modes of operation to help users better understand and work with Linux commands.

## Features

- Command explanations and historical context
- Command summarization (brief and detailed)
- Command cheatsheet generation
- System administration assistance
- Command troubleshooting
- Command discovery
- Task planning assistance

## Prerequisites

- Python 3.7+
- Ollama installed and running (https://ollama.ai) (or run itnwith docker)
- The required LLM model pulled via Ollama (default: qwen2.5:14b-instruct-q4_1) I would recoment using and 'Instruct' model if you want to change the model.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/superman.git
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

## Configuration

The default model is set to `qwen2.5:14b-instruct-q4_1`. To use a different model, modify the `model_name` parameter in `superman.py`:

```python
def __init__(self, model_name='your-preferred-model', mode='default'):
```

## Usage Examples

1. Get information about a command:
```bash
superman ls
```
Output:
```
ls is a fundamental command used to list directory contents. It was first introduced in AT&T UNIX and has been a core utility since then.
The command can show file permissions, sizes, and modification times with various flags.
Common usage includes ls -la for detailed listings and ls -R for recursive directory traversal.
```

2. Get a brief summary:
```bash
superman wget --shortsum
```
Output:
```
wget is a command-line utility for retrieving files using HTTP, HTTPS, and FTP protocols.
```

3. Generate a command cheatsheet:
```bash
superman tar -c
```
Output:
```
TAR COMMAND CHEATSHEET
---------------------
Common flags:
-c: Create archive
-x: Extract archive
-v: Verbose output
-f: Specify filename
-z: Use gzip compression

Common usage:
tar -czf archive.tar.gz files/    # Create compressed archive
tar -xzf archive.tar.gz           # Extract compressed archive

Best practices:
- Always specify the output file with -f
- Use -z for .gz compression
- Test archives after creation
```

4. Get help with a system administration task:
```bash
superman -a "How do I find large files on my system?"
```
Output:
```
Here's how to find large files:

• Using find:
  find / -type f -size +100M -exec ls -lh {} \;

• Using du:
  du -h / | sort -rh | head -n 20

• Quick solution:
  ncdu / --exclude /proc --exclude /sys
```

5. Analyze recent commands for troubleshooting:
```bash
superman -t 5
```

## Available Options

- `-s, --summarize`: Detailed command summary
- `--shortsum`: One-line command summary
- `-c, --cheat`: Generate command cheatsheet
- `-a, --assistant`: General system administration help
- `-f, --find`: Discover commands for specific tasks
- `-t, --trouble`: Analyze recent commands
- `-p, --plan`: Create task execution plan

## Limitations

- Requires Ollama to be running
- Response quality depends on the LLM model used
- May have longer response times with larger models

# Docker
Install docker, then run the run-superman.sh script.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
