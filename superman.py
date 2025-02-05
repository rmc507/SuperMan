from ollama import chat
import argparse
import time
import os
import sys
import traceback

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
    '''
}


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
    def __init__(self, model_name='qwen2.5:14b-instruct-q4_1', mode='default'):
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

    elif args.summarize:
        suman.set_mode('summarize')
        if args.assistant:
            prompt = f"{command}. Additional request: {args.assistant}"
        else:
            prompt = command
    elif args.shortsum:
        suman.set_mode('shortsum')
        if args.assistant:
            prompt = f"{command}. Additional request: {args.assistant}"
        else:
            prompt = command
    elif args.cheat:
        suman.set_mode('cheatsheet')
        if args.assistant:
            prompt = f"{command}. Additional request: {args.assistant}"
        else:
            prompt = command
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
