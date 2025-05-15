import argparse
from sqlmap_ai.local_llm_handler import LocalLLM

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Use local LLM instead of OpenAI")
    args = parser.parse_args()

    prompt = "Analyze this SQLMap output: \n<sqlmap log here>"

    if args.local:
        llm = LocalLLM()
    else:
        from sqlmap_ai.openai_handler import OpenAIHandler
        llm = OpenAIHandler()

    response = llm.generate_response(prompt)
    print("\n[+] LLM Response:\n", response)

if __name__ == "__main__":
    main()
