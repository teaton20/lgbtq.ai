from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        result = subprocess.run(
                    ["ollama", "run", "llama3.2:latest", message],
                    capture_output=True,
                    text=True,
                    check=True
                )
        print("STDERR:", result.stderr)  # For debugging purposes
        response_text = result.stdout
        return jsonify({"response": response_text})
    except Exception as e:
        print("Subprocess error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
