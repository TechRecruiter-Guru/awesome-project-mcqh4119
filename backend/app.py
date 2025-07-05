from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from awesome-project-mcqh4119!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)