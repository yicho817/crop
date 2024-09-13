from flask import Flask, request, jsonify
import zipfile
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "API is running"

if __name__ == '__main__':
    app.run(debug=True)
