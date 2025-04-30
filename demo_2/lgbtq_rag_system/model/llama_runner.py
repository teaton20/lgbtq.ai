# lgbtq_rag_system/model/llama_runner.py
import subprocess

def run_llm(prompt):
    """
    Calls the local LLM (e.g., via the Ollama CLI) with the given prompt.
    The prompt is encoded and sent via subprocess. Adjust parameters as needed.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2", "options:num_predict:100"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        output = result.stdout.decode().strip()
        if output:
            return output
        else:
            return "No response from the local LLM."
    except Exception as e:
        # If an error occurs during LLM invocation, return an error message.
        return f"Error calling LLM: {e}"