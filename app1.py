from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chattf import process_message

app = Flask(__name__)
CORS(app)

@app.get("/")
@app.get("/index1.html")
def index_get():
    return render_template("index1.html")

@app.route("/predict", methods=["POST"])
def predict():
    text = request.get_json().get("message")
    
    if not text:
        return jsonify({"error": "No message provided"}), 400
    
    # Process the message (assuming process_message returns a response to the message)
    response = process_message(text)
    
    # Return the response to the client immediately
    message = {"answer": response}
    
    return jsonify(message)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
