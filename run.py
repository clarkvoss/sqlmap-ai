import argparse
import os

def read_sqlmap_output():
    print("Enter path to your SQLMap output file or press Enter to paste logs:")
    path = input("Path: ").strip()

    if path and os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    else:
        print("Paste your SQLMap logs below. Press Ctrl+D (Linux/macOS) or Ctrl+Z (Windows) then Enter to finish:")
        try:
            return "".join(iter(input, ""))
        except EOFError:
            return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Use local LLM instead of OpenAI")
    args = parser.parse_args()

    sqlmap_output = read_sqlmap_output()

    if not sqlmap_output.strip():
        print("[-] No SQLMap output provided.")
        return

    if args.local:
        from sqlmap_ai.local_llm_handler import LocalLLM
        llm = LocalLLM()
    else:
        from sqlmap_ai.openai_handler import OpenAIHandler
        llm = OpenAIHandler()

    prompt = "Analyze the following SQLMap output and explain findings:\n" + sqlmap_output
    response = llm.generate_response(prompt)

    print("\n[+] LLM Response:\n")
    print(response)

if __name__ == "__main__":
    main()

