from transformers import AutoTokenizer, AutoModelForCausalLM

class LocalLLM:
    def __init__(self, model_name="microsoft/phi-2"):
        print(f"[+] Loading local LLM: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype="auto"
        )
        self.model.eval()

    def generate_response(self, prompt: str, max_tokens=512):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=max_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
