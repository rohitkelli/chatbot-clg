import json
import pickle
import numpy as np
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

# Download NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Load Excel File
file_path = r"Book2.xlsx"
df = pd.read_excel(file_path)

# Ensure required columns exist
if 'Patterns' not in df.columns or 'Tag' not in df.columns:
    raise ValueError("Required columns ('Patterns' and 'Tag') not found in the Excel file")

# Convert columns to strings and handle missing values
df['Patterns'] = df['Patterns'].astype(str).fillna('')
df['Tag'] = df['Tag'].astype(str).fillna('')

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

# Process each row in the Excel file
for index, row in df.iterrows():
    patterns = row['Patterns'].split('|')  # Assuming patterns are separated by '|'
    tag = row['Tag']

    for pattern in patterns:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, tag))

        if tag not in classes:
            classes.append(tag)

# Lemmatize words, remove duplicates
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))
classes = sorted(set(classes))

# Save words and classes
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Create training data
training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]

    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

# Convert training data to numpy arrays
train_x = np.array([item[0] for item in training])
train_y = np.array([item[1] for item in training])

# Define the model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile the model
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train the model
hist = model.fit(train_x, train_y, epochs=150, batch_size=5, verbose=1)

# Save the model
model.save('chatbot_model.h5')
print("Model trained and saved successfully!")