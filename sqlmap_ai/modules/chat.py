from sqlmap_ai.local_llm_handler import LocalLLM

def interactive_mode():
    llm = LocalLLM()
    history = []
    print("[+] Interactive Chat Mode (type 'exit' to quit)")
    while True:
        try:
            user_input = input("ask> ")
            if user_input.strip().lower() in ['exit', 'quit']:
                break
            prompt = "\n".join(history + [f"User: {user_input}"])
            response = llm.generate_response(prompt)
            print("AI:", response)
            history.append(f"User: {user_input}")
            history.append(f"AI: {response}")
        except KeyboardInterrupt:
            break
