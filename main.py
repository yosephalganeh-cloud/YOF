#!/usr/bin/env python3
"""
YoFsociety - Personal Hacker & Developer Terminal AI
----------------------------------------------------
Works on any terminal (Linux, Windows, macOS, Termux, Pydroid 3).
Connects to OpenRouter free models and saves API key locally.
"""

import os
import sys
import json
import requests

# Cross-platform color support
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

# Files & URLs
CONFIG_FILE = os.path.expanduser("~/.yofsociety_config.json")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"
HISTORY_LIMIT = 20
TIMEOUT_SECONDS = 60

DEFAULT_SYSTEM_PROMPT = (
    "You are YoFsociety AI, a specialized developer and hacker assistant. "
    "You help users by generating Python scripts, finding GitHub repositories, "
    "and answering technical questions. You MUST always answer in Amharic language. "
    "Keep your answers clear, practical, precise, and concise."
)

BANNER = f"""{Fore.GREEN}{Style.BRIGHT}
██╗██╗   ██╗███████╗██████╗  ██████╗ ███████╗██╗███████╗████████╗██╗   ██╗
██║██║   ██║██╔════╝██╔══██╗██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
██║██║   ██║█████╗  ██████╔╝██║   ██║███████╗██║█████╗     ██║    ╚████╔╝ 
██║██║   ██║██╔══╝  ██╔══██╗██║   ██║╚════██║██║██╔══╝     ██║     ╚██╔╝  
██║╚██████╔╝██║     ██║  ██║╚██████╔╝███████║██║███████╗   ██║      ██║   
╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
{Fore.CYAN}              [ Personal Terminal AI for Hackers & Devs ]
{Fore.YELLOW}                    [ Language Mode: Amharic ]
{Style.RESET_ALL}"""


def get_api_key():
    """Retrieves API Key from environment or local config; asks user if missing."""
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

    print(f"{Fore.YELLOW}[!] OpenRouter API Key አልተገኘም።{Fore.RESET}")
    print(f"{Fore.CYAN}API Key ከ https://openrouter.ai/keys በነፃ ማግኘት ይችላሉ።{Fore.RESET}\n")
    
    user_key = input(f"{Fore.GREEN}እባክዎ OpenRouter API Key ያስገቡ: {Fore.RESET}").strip()
    if not user_key:
        print(f"{Fore.RED}[!] API Key ስላልገባ ፕሮግራሙ ይዘጋል።{Fore.RESET}")
        sys.exit(1)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": user_key}, f)
        print(f"{Fore.GREEN}[✓] API Key በ {CONFIG_FILE} ላይ ተቀምጧል!\n{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.RED}[!] Key ማስቀመጥ አልተቻለም: {e}{Fore.RESET}\n")

    return user_key


def ask(history, api_key):
    """Sends chat payload to OpenRouter API."""
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
        raise RuntimeError("የገባው API key ትክክል አይደለም። እባክዎ ~/.yofsociety_config.json ያፅዱ ወይም አዲስ Key ያስገቡ።")
    if resp.status_code == 429:
        raise RuntimeError("የጥያቄ ብዛት አልፏል (Rate limited) — ትንሽ ቆይተው ደግመው ይሞክሩ።")
    resp.raise_for_status()

    return resp.json()["choices"][0]["message"]["content"]


def print_help():
    print(f"""
{Fore.YELLOW}ትእዛዛት (Commands):{Fore.RESET}
  {Fore.GREEN}/persona <text>{Fore.RESET}  - የ AI ባህሪ ወይም ሚና ለመቀየር
  {Fore.GREEN}/key            {Fore.RESET}  - የተቀመጠውን API Key ለመቀየር
  {Fore.GREEN}/clear          {Fore.RESET}  - የቆየውን ንግግር ለማፅዳት
  {Fore.GREEN}/help           {Fore.RESET}  - ይህንን መመሪያ ለማየት
  {Fore.GREEN}/exit           {Fore.RESET}  - ከፕሮግራሙ ለመውጣት (exit, quit)
""")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    api_key = get_api_key()

    print(f"{Fore.GREEN}=== YoFsociety ዝግጁ ነው! ==={Fore.RESET}")
    print("ለማንኛውም ጥያቄ ጽፈው Enter ይጫኑ። ለትእዛዛት /help ብለው ይጻፉ።\n")

    system_prompt = DEFAULT_SYSTEM_PROMPT
    history = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{Fore.GREEN}{Style.BRIGHT}YoFsociety > {Style.RESET_ALL}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}መልካም ጊዜ! Bye!{Fore.RESET}")
            break

        if not user_input:
            continue

        low = user_input.lower()

        if low in ("/exit", "exit", "quit"):
            print(f"{Fore.YELLOW}መልካም ጊዜ! Bye!{Fore.RESET}")
            break

        if low == "/help":
            print_help()
            continue

        if low == "/clear":
            history = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}[የቀደመው ንግግር ተፅድቷል]{Fore.RESET}\n")
            continue

        if low == "/key":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            api_key = get_api_key()
            continue

        if user_input.startswith("/persona "):
            system_prompt = user_input[len("/persona "):].strip()
            history = [{"role": "system", "content": system_prompt}]
            print(f"{Fore.YELLOW}[Persona ተቀይሯል። ንግግሩ ከአዲስ ተጀምሯል።]{Fore.RESET}\n")
            continue

        history.append({"role": "user", "content": user_input})
        trimmed = [history[0]] + history[-HISTORY_LIMIT:]

        print(f"{Fore.CYAN}በማሰብ ላይ...{Fore.RESET}", end="\r")

        try:
            reply = ask(trimmed, api_key)
            print(" " * 20, end="\r") # Clean "በማሰብ ላይ..." line
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}[ስህተት: ኢንተርኔት ፍጥነት አነስተኛ ነው ወይም አላገናኘም]{Fore.RESET}\n")
            continue
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}[ስህተት: የኢንተርኔት ግንኙነት የለም]{Fore.RESET}\n")
            continue
        except Exception as e:
            print(f"{Fore.RED}[ስህተት: {e}]{Fore.RESET}\n")
            continue

        history.append({"role": "assistant", "content": reply})
        print(f"{Fore.CYAN}{Style.BRIGHT}AI:{Style.RESET_ALL}\n{reply}\n")


if __name__ == "__main__":
    main()
