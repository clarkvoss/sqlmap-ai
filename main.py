import argparse
from sqlmap_ai.modules.runner import run_assisted_scan
from sqlmap_ai.modules.burp_parser import run_burp_analysis
from sqlmap_ai.modules.chat import interactive_mode

def main():
    parser = argparse.ArgumentParser(description="sqlmap-ai Pro: AI-Augmented SQLi Engine")
    parser.add_argument("--scan", action="store_true", help="Run assisted SQLi analysis")
    parser.add_argument("--burp", type=str, help="Analyze a Burp Suite XML export file")
    parser.add_argument("--chat", action="store_true", help="Enter interactive chat mode")
    parser.add_argument("--local", action="store_true", help="Use local LLM (Phi-2)")

    args = parser.parse_args()

    if args.scan:
        run_assisted_scan(local=args.local)
    elif args.burp:
        run_burp_analysis(args.burp)
    elif args.chat:
        interactive_mode()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
