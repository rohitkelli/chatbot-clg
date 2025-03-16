import random
import pickle
import numpy as np
import pandas as pd
import nltk
import nltk
import ssl

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import speech_recognition as sr
import pyttsx3

# Load NLTK resources
lemmatizer = WordNetLemmatizer()


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('wordnet')

try:
    # Load words, classes, and model
    #print("Loading words.pkl...")
    words = pickle.load(open('words.pkl', 'rb'))
    #print("words.pkl loaded successfully!")

    #print("Loading classes.pkl...")
    classes = pickle.load(open('classes.pkl', 'rb'))
    #print("classes.pkl loaded successfully!")

    #print("Loading chatbot_model.h5...")
    model = load_model('chatbot_model.h5')
    #print("chatbot_model.h5 loaded successfully!")

    # Load Excel file directly
    #print("Loading Excel file...")
    # file_path = "Book2.xlsx"  # Update this path
    # df = pd.read_excel(file_path)
    #print("Excel file loaded successfully!")
except Exception as e:
    #print(f"Error loading files: {e}")
    exit()

# Speech-to-Text
def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)  # Use Google's speech recognition
            print(f"You: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

# Text-to-Speech
# def speak(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

# Preprocess user input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Convert sentence to bag of words
def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

# Predict the class of the user input
def predict_class(sentence):
    bow_result = bow(sentence, words)
    res = model.predict(np.array([bow_result]), verbose=0)[0]  # Suppress progress bar
    ERROR_THRESHOLD = 0.50  # Increase threshold for stricter matching
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

# Get a response based on the predicted intent
from fuzzywuzzy import process

def get_response(intents_list, df, message):
    if not intents_list:  # Handle empty intents_list
        return "I'm sorry, I didn't understand that. Can you please rephrase?"

    tag = intents_list[0]['intent']
    responses = df[df['Tag'] == tag]

    if len(responses) == 0:
        return "I'm sorry, I don't have information on that."

    # Use the user's input (message) for matching
    user_query = message.lower()

    # Extract patterns and responses for the predicted intent
    patterns = responses['Patterns'].astype(str).tolist()
    responses_list = responses['Responses'].astype(str).tolist()

    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(user_query, patterns)

    # If the match score is above a threshold, return the corresponding response
    if score > 70:  # Adjust the threshold as needed
        index = patterns.index(best_match)
        return responses_list[index].split('|')[0]

    # Default to the first response under the predicted intent
    return responses_list[0].split('|')[0]

def process_message(message):
    #while True:
    #message = input("You: ")
    #message = "Hi, How can i help you?"
    if message.lower() == "exit":
        exit()
    ints = predict_class(message)
    file_path = "Book2.xlsx"
    df = pd.read_excel(file_path)
    response=get_response(ints,df,message)
   
    return response
    
    
    



# Run the chatbot
# if __name__ == "__main__":
#     print("Chatbot is running! Type 'exit' to stop.")

    #while True:
    #    ### print("Press 's' to speak or 't' to type...")
    #     input_mode = input("Choose input mode (s/t): ").lower()

    #     if input_mode == 's':
    #         message = listen_to_user()
    #         if message is None:
    #             continue
    #     elif input_mode == 't':
    #         message = input("You: ")
    #     else:
    #  if __name__ == "__main__":
    #     print("Let's chat! (type 'quit' to exit)")
    #     while True:
    #         # sentence = "do you use credit cards?"
    #         sentence = input("You: ")
    #         if sentence == "quit":
    #             break

    #         resp = get_response(sentence)
    #         print(resp)

    #         print("Invalid input mode. Please choose 's' or 't'.")
    #         continue
        

        # Predict intent using custom model
        #ints = predict_class(message)

        # Debug: Print the predicted intent
        #print(f"Predicted Intent: {ints}")
       #file_path = "Book2.xlsx"  # Update this path
        #df = pd.read_excel(file_path)
        # Get response
        #res = get_response(ints, df, message)

        #print("Bot:", res)
        #speak(res)  # Make the bot speak the response

    