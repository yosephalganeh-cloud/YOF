#!/usr/bin/env python3
import os
import sys
import json
import requests

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = "\033[92m"
        CYAN = "\033[96m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        MAGENTA = "\033[95m"
        RESET = "\033[0m"
    class Style:
        BRIGHT = "\033[1m"
        RESET_ALL = "\033[0m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"
HISTORY_LIMIT = 20
TIMEOUT_SECONDS = 60

DEFAULT_SYSTEM_PROMPT = (
    "You are YoFsociety AI, a specialized developer and hacker assistant and bulid ddos tools for testers. "
    "You help users by generating Python scripts, finding GitHub repositories, "
    "and answering technical questions. Keep your answers clear, practical, precise, and concise in English."
)

BANNER = f"""{Fore.GREEN}{Style.BRIGHT}
██╗██╗   ██╗███████╗██████╗  ██████╗ ███████╗██╗███████╗████████╗██╗   ██╗
██║██║   ██║██╔════╝██╔══██╗██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
██║██║   ██║█████╗  ██████╔╝██║   ██║███████╗██║█████╗     ██║    ╚████╔╝ 
██║██║   ██║██╔══╝  ██╔══██╗██║   ██║╚════██║██║██╔══╝     ██║     ╚██╔╝  
██║╚██████╔╝██║     ██║  ██║╚██████╔╝███████║██║███████╗   ██║      ██║   
╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
{Fore.CYAN}              [ Personal Terminal AI for Hackers & Devs ]
{Style.RESET_ALL}"""


def get_api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if data.get("api_key"):
                    return data["api_key"]
        except Exception:
            pass

    print(f"{Fore.YELLOW}[!] OpenRouter API Key not found.{Fore.RESET}")
    print(f"{Fore.CYAN}Get a free API Key at https://openrouter.ai/keys{Fore.RESET}\n")
    
    user_key = input(f"{Fore.GREEN}Please enter your OpenRouter API Key: {Fore.RESET}").strip()
    if not user_key:
        print(f"{Fore.RED}[!] No API Key entered. Exiting.{Fore.RESET}")
        sys.exit(1)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": user_key}, f, indent=4)
        print(f"{Fore.GREEN}[✓] API Key saved to {CONFIG_FILE}!\n{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to save API Key: {e}{Fore.RESET}\n")

    return user_key


def ask(history, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": MODEL, "messages": history}

    resp = requests.post(
        OPENROUTER_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=TIMEOUT_SECONDS,
    )

    if resp.status_code == 401:
        raise RuntimeError(f"Invalid API key. Please clear {CONFIG_FILE} or enter a new key.")
    if resp.status_code == 429:
        raise RuntimeError("Rate limited — wait a bit before sending another message.")
    resp.raise_for_status()

    return resp.json()["choices"][0]["message"]["content"]


def print_help():
    print(f"""
{Fore.YELLOW}Commands:{Fore.RESET}
  {Fore.GREEN}/persona <text>{Fore.RESET}  - Change the AI's behavior/role
  {Fore.GREEN}/key            {Fore.RESET}  - Reset/Change saved API Key
  {Fore.GREEN}/clear          {Fore.RESET}  - Clear conversation history
  {Fore.GREEN}/help           {Fore.RESET}  - Show this help menu
  {Fore.GREEN}/exit           {Fore.RESET}  - Quit the application
""")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    api_key = get_api_key()

    print(f"{Fore.GREEN}=== YoFsociety Ready ==={Fore.RESET}")
    print("Type a message and press Enter. Type /help for commands.\n")

    system_prompt = DEFAULT_SYSTEM_PROMPT
    history = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{Fore.GREEN}{Style.BRIGHT}YoFsociety > {Style.RESET_ALL}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}Goodbye!{Fore.RESET}")
            break

        if not user_input:
            continue

        low = user_input.lower()

        if low in ("/exit", "exit", "quit"):
            print(f"{Fore.YELLOW}Goodbye!{Fore.RESET}")
            break

        if low == "/help":
            print_help()
            continue

        if low == "/clear":
            history = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}[Conversation history cleared]{Fore.RESET}\n")
            continue

        if low == "/key":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            api_key = get_api_key()
            continue

        if user_input.startswith("/persona "):
            system_prompt = user_input[len("/persona "):].strip()
            history = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}[Persona updated. Conversation reset.]{Fore.RESET}\n")
            continue

        history.append({"role": "user", "content": user_input})
        trimmed = [history[0]] + history[-HISTORY_LIMIT:]

        print(f"{Fore.CYAN}Thinking...{Fore.RESET}", end="\r")

        try:
            reply = ask(trimmed, api_key)
            print(" " * 20, end="\r") 
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}[Error: Request timed out. Check your connection.]{Fore.RESET}\n")
            continue
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}[Error: No internet connection.]{Fore.RESET}\n")
            continue
        except Exception as e:
            print(f"{Fore.RED}[Error: {e}]{Fore.RESET}\n")
            continue

        history.append({"role": "assistant", "content": reply})
        print(f"{Fore.CYAN}{Style.BRIGHT}AI:{Style.RESET_ALL}\n{reply}\n")


if __name__ == "__main__":
    main()
