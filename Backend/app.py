from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from llm import get_insights


app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/api", methods=["POST"])
def api():
    data = request.files.get("image")
    output = get_insights(data.read())
    return jsonify(output)


if __name__ == "__main__":
    app.run(debug=True)
