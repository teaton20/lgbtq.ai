import logging
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    app.logger.info("Rendering home page")
    return render_template("index.html")

# Example API endpoint for dynamic interactions
@app.route("/api/demo", methods=["GET"])
def demo_api():
    data = {"message": "Hello from the API!"}
    return jsonify(data)

# Error handler for 404 errors
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)