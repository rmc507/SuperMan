from ollama import chat
import argparse
import time
import os
import sys
import json
import subprocess
import shlex
import random
import string

SYSTEM_MESSAGES = {
    'default': '''
    Your purpose it to take a bash command from the user, and interpret their question to the best of your ability. Do not output any warnings or notes. If no question is provided, output a summary of what that command is capable of
    You should also think about the history of that command and tell the user some interesting facts about it. Keep your output breif.
    ''',
    'summarize': '''
    Your purpose is to take a bash command from the user and sumarise it.
    You need to tell the user what the command does, and how to use it. Summarise the capabilities and use cases.
    Please keep your response to the point while maintinaing all neccisary information.
    You are rewuired to summarise the capabilities and the use cases.
    ommiting the use cases and capabilities is not allowed.
    please keep the output as breif as possible
    ''',
    'shortsum': '''
    Your purpose is to take a bash command from the user and return a one sentince summary of what that command is used for. If that command does not exist,
    Tell the user that the command does not exist. Do not output more than one line.
    ''',
    'cheatsheet': '''
    Your purpose is to take a bash command from the user and create a one page cheat sheet for the user to reference.
    Include all important flags and outline the best use cases and best practices for the user to follow.
    ''',
    'assistant': '''
    You are an assistant for a linux system administrator.
    Your primary purpose is to answer questions he may have about the system.
    respond with more information than is neccicary.
    Lay out the steps to solve the users problem in a well formatted bulleted list.
    Do not focus on uncommon commands, only use the most popular commands.
    Keep your output breif while still addressing the question.
    ''',
    'trouble': '''
        Your purpose is to analyze a list of recent shell commands and:
        1. Identify any potential issues or errors in the command sequence
        2. Output the corrected command in its own line
        Keep your analysis concise and focused on helping resolve any potential issues.
        ''',
    'find': '''
    Your purpose is to take the user question and come up with the top three linux commands to solve that problem.
    You should list the three commands on one line each, followed directly with a description of how it works and how it solves the users problem
    do not output any warnings or notes.
    ''',
    'plan': '''
    Your purpose is to create a step by step plan to solve the users problem.
    The user needs help with linux, so please solve the problem with a focus on that.
    Do not output any warnings or notes.
    Your output should be well formatted, with bullet points and headers.
    ''',
    'exec': '''
    You are a command execution assistant. Only execute commands that are safe.
    When given a description of what needs to be done,
    you should respond with a JSON object containing the command to execute. Format your response as:
    {"command": "the_command_to_execute"}
    Only respond with the JSON object, no other text.
    Assume that the command should be ran in the current directory, unless other specified.'''
}

def generate_confirmation_code() -> str:
    """Generate a random 5-character string of letters and numbers"""
    #characters = string.ascii_letters + string.digits
    #return ''.join(random.choice(characters) for _ in range(5))
    return 'Allow'



def is_command_safe(command: str) -> tuple[bool, str, bool]:
    """
    Check if a command is safe to execute.
    Returns a tuple of (is_safe, reason, requires_confirmation)
    """
    # Split command into parts for better analysis
    cmd_parts = shlex.split(command.lower())
    if not cmd_parts:
        return False, "Empty command", False

    base_cmd = cmd_parts[0]
    BLACKLIST = {
        # File Operations
        'rm': 'File deletion command is not allowed',
        'mv': 'Moving files is not allowed',
        'cp': 'Copying files is not allowed',
        'shred': 'File shredding is not allowed',
        'srm': 'Secure file deletion is not allowed',
        'unlink': 'File unlinking is not allowed',
        'rename': 'File renaming is not allowed',

        # System Administration
        'sudo': 'Elevated privileges are not allowed',
        'su': 'Switching users is not allowed',
        'chroot': 'Changing root is not allowed',
        'passwd': 'Password changes are not allowed',
        'mkfs': 'Filesystem formatting is not allowed',
        'fdisk': 'Disk partitioning is not allowed',
        'parted': 'Disk partitioning is not allowed',
        'mount': 'Mounting filesystems is not allowed',
        'umount': 'Unmounting filesystems is not allowed',
        'systemctl': 'System control is not allowed',
        'service': 'Service management is not allowed',
        'init': 'Init commands are not allowed',
        'systemd': 'Systemd commands are not allowed',

        # Process Management
        'kill': 'Process termination is not allowed',
        'pkill': 'Process killing is not allowed',
        'killall': 'Process killing is not allowed',
        'renice': 'Process priority modification is not allowed',
        'nice': 'Process priority modification is not allowed',

        # System Control
        'shutdown': 'System shutdown is not allowed',
        'reboot': 'System reboot is not allowed',
        'poweroff': 'System power off is not allowed',
        'halt': 'System halt is not allowed',

        # Network Operations
        'wget': 'Downloading files is not allowed',
        'curl': 'Downloading files is not allowed',
        'nc': 'Netcat operations are not allowed',
        'netcat': 'Netcat operations are not allowed',
        'ssh': 'SSH operations are not allowed',
        'ftp': 'FTP operations are not allowed',
        'sftp': 'SFTP operations are not allowed',
        'iptables': 'Firewall modifications are not allowed',
        'ufw': 'Firewall modifications are not allowed',
        'tcpdump': 'Network packet capture is not allowed',

        # File Permissions and Ownership
        'chmod': 'Changing file permissions is not allowed',
        'chown': 'Changing file ownership is not allowed',
        'chgrp': 'Changing group ownership is not allowed',
        'umask': 'Changing file creation mask is not allowed',

        # Package Management
        'apt': 'Package management is not allowed',
        'apt-get': 'Package management is not allowed',
        'dpkg': 'Package management is not allowed',
        'yum': 'Package management is not allowed',
        'dnf': 'Package management is not allowed',
        'pacman': 'Package management is not allowed',
        'pip': 'Python package management is not allowed',
        'npm': 'Node.js package management is not allowed',

        # Dangerous Operations
        'dd': 'Direct disk operations are not allowed',
        'mkswap': 'Swap creation is not allowed',
        'swapoff': 'Swap manipulation is not allowed',
        'swapon': 'Swap manipulation is not allowed',
        'losetup': 'Loop device setup is not allowed',
        'blockdev': 'Block device operations are not allowed',

        # Shell Operations
        'eval': 'Eval commands are not allowed',
        'exec': 'Exec commands are not allowed',
        'source': 'Sourcing files is not allowed',
        '.': 'Sourcing files is not allowed',
        'alias': 'Creating aliases is not allowed',

        # User Management
        'useradd': 'User creation is not allowed',
        'userdel': 'User deletion is not allowed',
        'usermod': 'User modification is not allowed',
        'groupadd': 'Group creation is not allowed',
        'groupdel': 'Group deletion is not allowed',
        'groupmod': 'Group modification is not allowed',

        # System Information Leakage Prevention
        'uname': 'System information disclosure is not allowed',
        'hostname': 'System information disclosure is not allowed',
        'id': 'User information disclosure is not allowed',
        'who': 'User information disclosure is not allowed',
        'w': 'User information disclosure is not allowed',
        'last': 'Login information disclosure is not allowed',

        # File Creation/Modification
        'touch': 'File creation is not allowed',
        'truncate': 'File truncation is not allowed',
        'mknod': 'Device file creation is not allowed',
        'mkfifo': 'FIFO creation is not allowed',

        # Compression/Archive Operations
        'tar': 'Archive operations are not allowed',
        'gzip': 'Compression operations are not allowed',
        'gunzip': 'Decompression operations are not allowed',
        'zip': 'Compression operations are not allowed',
        'unzip': 'Decompression operations are not allowed',

        # Editor Access
        'vi': 'Text editor access is not allowed',
        'vim': 'Text editor access is not allowed',
        'nano': 'Text editor access is not allowed',
        'emacs': 'Text editor access is not allowed',
        'ed': 'Text editor access is not allowed',
        'git': 'Git Access is not allowed.'
    }
    # Check for suspicious patterns first
    dangerous_patterns = [
            ('$(', 'Command substitution is not allowed'),
            ('`', 'Backtick command substitution is not allowed'),
            ('&&', 'Command chaining is not allowed'),
            ('||', 'Command chaining is not allowed'),
            (';', 'Command chaining is not allowed'),
            ('| ', 'Piping is not allowed'),
            ('> /', 'Writing to root directory is not allowed'),
            ('> /dev', 'Writing to devices is not allowed'),
        ]

    for pattern, reason in dangerous_patterns:
        if pattern in command:
            return True, reason, True

    # Check if the base command is in blacklist
    if base_cmd in BLACKLIST:
        return True, BLACKLIST[base_cmd], True  # Command is blacklisted, requires confirmation

    # Check for direct path execution
    if '/' in base_cmd:
        return False, "Direct path execution is not allowed", False

    # If command passes all checks and isn't blacklisted
    return True, "Command is safe", False

def execute_command(command: str) -> tuple[bool, str]:
    """
    Execute a command with confirmation for blacklisted or dangerous patterns
    Returns a tuple of (success, output/error_message)
    """
    is_safe, reason, requires_confirmation = is_command_safe(command)

    try:
        if requires_confirmation or not is_safe:  # Changed to handle both cases
            # Generate and display confirmation code
            confirmation_code = generate_confirmation_code()
            print("\n⚠️  WARNING: This command requires confirmation!")
            print(f"Reason: {reason}")
            print(f"\nTo proceed, please type this confirmation code: {confirmation_code}")

            user_input = input("Confirmation code: ")

            if user_input.strip() != confirmation_code:
                return False, "Confirmation code incorrect. Command execution cancelled."

            print("\nConfirmation code correct. Executing command...")

        # Execute command with real-time output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        output = []
        # Stream stdout in real-time
        while True:
            line = process.stdout.readline()
            if line:
                print(line, end='', flush=True)
                output.append(line)
            if not line and process.poll() is not None:
                break

        # Get any remaining stderr
        stderr = process.stderr.read()
        if stderr:
            print(stderr, end='', flush=True)
            output.append(stderr)

        if process.returncode == 0:
            return True, ''.join(output)
        else:
            return False, f"Command failed: {''.join(output)}"

    except subprocess.TimeoutExpired:
        return False, "Command timed out after 10 seconds"
    except Exception as e:
        return False, f"Error executing command: {str(e)}"

def get_recent_commands(num_commands):
    """Get the specified number of most recent shell commands."""
    try:
        history_file = "/tmp/superman_current_history"
        if not os.path.exists(history_file):
            return []

        with open(history_file, 'r') as f:
            history_lines = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) >= 2:  # If we have both number and command
                    cmd = parts[1]
                    if cmd and not 'superman' in cmd.lower() and not 'test' in cmd.lower():
                        history_lines.append(cmd)

            return history_lines[-num_commands:]

    except Exception as e:
        print(f"Error reading history: {str(e)}", file=sys.stderr)
        return []

class SuperMan:  # command-r:35b-08-2024-q2_K        hf.co/OzgurEnt/OZGURLUK-GPT-LinuxGeneral:F16     mistral-nemo
    def __init__(self, model_name='llama3.1:8b-instruct-q4_0', mode='default'):
        self.model = model_name
        self.system_message = SYSTEM_MESSAGES[mode]

    def set_mode(self, mode):
        """Update the system message based on the mode"""
        self.system_message = SYSTEM_MESSAGES.get(mode, SYSTEM_MESSAGES['default'])

    def generate_response(self, user_input, stream=True):
        try:
            start_time = time.time()
            full_response = ""

            for chunk in chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_message},
                    {'role': 'user', 'content': user_input}
                ],
                stream=stream,
            ):
                current_time = time.time()
                if current_time - start_time > 120:  # 2-minute timeout
                    print("\n[Response timed out after 2 minutes]")
                    break

                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    print(content, end='', flush=True)
                    full_response += content

            return full_response

        except Exception as e:
            print(f"\nError: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return "I apologize, but I encountered an error. Please try again."


def main():
    parser = argparse.ArgumentParser(description='Superman Manual Entry Assistant')
    parser.add_argument('command', nargs='*', help='The command that you would like the assistant to process.')
    parser.add_argument('-s', '--summarize', action='store_true', help='Tell the model to summarise the command')
    parser.add_argument('--shortsum', action='store_true', help='Tell the model to make a short summary of the command')
    parser.add_argument('-c', '--cheat', action='store_true', help="Have the model create a cheat sheet for the command")
    parser.add_argument('-a', '--assistant', nargs='?', const='', help="Talk directly with the model with whatever question you may have")
    parser.add_argument('-f', '--find', nargs='?', const='', help="Find the correct command to use for your problem")
    parser.add_argument('-t', '--trouble', type=int, nargs='?', const=10, help='Analyze the last N commands for troubleshooting (default: 10)')
    parser.add_argument('-p', '--plan', nargs='?', const='', help='Have the model make a plan to acomplish your goal')
    parser.add_argument('-e', '--exec', help='Execute a command based on the description provided')

    args = parser.parse_args()
    suman = SuperMan()

    command = ' '.join(args.command) if args.command else ""

    if args.trouble:
        recent_commands = get_recent_commands(args.trouble)
        if not recent_commands:
            print("\nNo recent commands found to analyze.")
            return
        command_history = "\n".join(recent_commands)
        if args.assistant:
            prompt = f"Please analyze these recent commands with this specific focus: {args.assistant}\n\nCommands:\n{command_history}"
        else:
            prompt = f"Please analyze these recent commands:\n{command_history}"
        suman.set_mode('trouble')
        suman.generate_response(prompt)
    elif args.exec:
            suman.set_mode('exec')
            response = suman.generate_response(f"Create a command that would: {args.exec}")
            try:
                # Extract the command from the response
                import re
                # Try to find JSON-like structure in the response
                json_match = re.search(r'\{.*\}', response)
                if json_match:
                    command_data = json.loads(json_match.group())
                    if "command" in command_data:
                        command = command_data["command"]
                        # Ask for confirmation

                        success, output = execute_command(command)
                        if success:
                            print("\nCommand executed successfully!")
                        else:
                            print("\nCommand execution failed:")
                            print(output)
                        return
                print("\nCouldn't parse response as a command.\n")
            except (json.JSONDecodeError, AttributeError):
                print("\nFailed to parse response as JSON.\n")
    else:
        # Set prompt based on arguments
        if args.summarize:
            suman.set_mode('summarize')
            prompt = f"{command}. Additional request: {args.assistant}" if args.assistant else command
        elif args.shortsum:
            suman.set_mode('shortsum')
            prompt = f"{command}. Additional request: {args.assistant}" if args.assistant else command
        elif args.cheat:
            suman.set_mode('cheatsheet')
            prompt = f"{command}. Additional request: {args.assistant}" if args.assistant else command
        elif args.assistant:
            suman.set_mode('assistant')
            prompt = args.assistant if args.assistant else command
        elif args.find:
            suman.set_mode('find')
            prompt = args.find
        elif args.plan:
            suman.set_mode('plan')
            prompt = args.plan
        else:
            prompt = command

        # Generate response
        suman.generate_response(prompt)
        print('\n')

if __name__ == '__main__':
    main()
