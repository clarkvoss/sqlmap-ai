import os
import subprocess
from sqlmap_ai.local_llm_handler import LocalLLM

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

def score_risk(response):
    if "password" in response.lower() or "credentials" in response.lower():
        return "🔴 High"
    elif "column" in response.lower() or "table" in response.lower():
        return "🟡 Medium"
    return "🟢 Low"

def run_assisted_scan(local=True):
    print("Enter path to your SQLMap output file or press Enter to paste logs:")
    path = input("Path: ").strip()

    if path and os.path.exists(path):
        with open(path, "r") as f:
            sqlmap_output = f.read()
    else:
        print("Paste your SQLMap logs below. Ctrl+D or Ctrl+Z to finish:")
        try:
            sqlmap_output = "".join(iter(input, ""))
        except EOFError:
            sqlmap_output = ""

    if not sqlmap_output.strip():
        print("[-] No SQLMap output provided.")
        return

    llm = LocalLLM()

    dbms = detect_dbms(sqlmap_output)
    vuln = is_vulnerable(sqlmap_output)
    tamper = suggest_tamper(sqlmap_output)
    strategy = next_steps(dbms)

    prompt = f"""You are an AI security assistant. SQLMap analysis shows:
- Vulnerability: {vuln}
- DBMS: {dbms}
- Suggested tamper: {tamper}
- Strategy: {strategy}

Suggest full SQLMap command and summarize the vulnerability:
SQLMap Output:
{sqlmap_output}
"""

    response = llm.generate_response(prompt)
    print("\n[+] AI Summary:\n", response)
    print("\n[+] Risk Level:", score_risk(response))

    print("\nDo you want to execute the suggested SQLMap command? (y/N)")
    choice = input("> ").strip().lower()
    if choice == "y":
        print("\n[!] Enter the full SQLMap target URL:")
        url = input("URL: ").strip()
        full_command = f"sqlmap -u {url} {strategy} {tamper}"
        print(f"\n[+] Running: {full_command}")
        subprocess.run(full_command, shell=True)
