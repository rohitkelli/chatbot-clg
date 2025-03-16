from flask import Flask, render_template, request, jsonify
from time import time
import pyttsx3
from flask_cors import CORS
#from flask_ngrok import run_with_ngrok
from flask_socketio import SocketIO, emit
from chattf import process_message

from threading import Thread



app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
#run_with_ngrok(app)

@socketio.on('message')
def handle_message(msg):
    response = process_message(msg)
    emit('response', {'answer': response})

def display_speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


@app.get("/")
@app.get("/index.html")
def index_get():
    return render_template("index.html")

@app.post("/predict")
@app.route("/predict", methods=["POST"])
def predict():
    text = request.get_json().get("message")
    
    if not text:
        return jsonify({"error": "No message provided"}), 400
    
    # Process the message (assuming process_message returns a response to the message)
    response = process_message(text)
    
    # Return the response to the client immediately
    message = {"answer": response}
    
    # Generate speech in the background
    speech_thread = Thread(target=display_speak, args=(response,))
    speech_thread.start()
    
    # Return the JSON response with the answer
    return jsonify(message)
if __name__ == "__main__":
    app.run(host='0.0.0.0')