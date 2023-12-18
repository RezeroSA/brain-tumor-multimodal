#OS libs
import os

#Deep learning libs
import re
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding
from keras.models import Sequential, load_model # Add 'load_model'
import pickle
import nltk
from nltk.stem import WordNetLemmatizer

# Keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename


imageModel = load_model('./model/imageModel.h5', compile=False)

imageModel.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

 # Load the vectoriser.
file = open('model/vectoriser-ngram-(1,2).pickle', 'rb')
vectoriser = pickle.load(file)
file.close()
# Load the LR Model.
file = open('model/Sentiment-LR.pickle', 'rb')
LRmodel = pickle.load(file)
file.close()

# Define a flask app
app = Flask(__name__)

# Defining dictionary containing all emojis with their meanings.
emojis = {':)': 'smile', ':-)': 'smile', ';d': 'wink', ':-E': 'vampire', ':(': 'sad', 
          ':-(': 'sad', ':-<': 'sad', ':P': 'raspberry', ':O': 'surprised',
          ':-@': 'shocked', ':@': 'shocked',':-$': 'confused', ':\\': 'annoyed', 
          ':#': 'mute', ':X': 'mute', ':^)': 'smile', ':-&': 'confused', '$_$': 'greedy',
          '@@': 'eyeroll', ':-!': 'confused', ':-D': 'smile', ':-0': 'yell', 'O.o': 'confused',
          '<(-_-)>': 'robot', 'd[-_-]b': 'dj', ":'-)": 'sadsmile', ';)': 'wink', 
          ';-)': 'wink', 'O:-)': 'angel','O*-)': 'angel','(:-D': 'gossip', '=^.^=': 'cat'}

## Defining set containing all stopwords in english.
stopwordlist = ['a', 'about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and','any','are', 'as', 'at', 'be', 'because', 'been', 'before',
             'being', 'below', 'between','both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each','few', 'for', 'from', 
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into','is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most','my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours','ourselves', 'out', 'own', 're',
             's', 'same', 'she', "shes", 'should', "shouldve",'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 
             'through', 'to', 'too','under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where','which','while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd","youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves']

def preprocess(textdata):
    processedText = []
    
    # Create Lemmatizer and Stemmer.
    wordLemm = WordNetLemmatizer()
    
    # Defining regex patterns.
    urlPattern        = r"((http://)[^ ]*|(https://)[^ ]*|( www\.)[^ ]*)"
    userPattern       = '@[^\s]+'
    alphaPattern      = "[^a-zA-Z0-9]"
    sequencePattern   = r"(.)\1\1+"
    seqReplacePattern = r"\1\1"
    
    for tweet in textdata:
        tweet = tweet.lower()
        
        # Replace all URls with 'URL'
        tweet = re.sub(urlPattern,' URL',tweet)
        # Replace all emojis.
        for emoji in emojis.keys():
            tweet = tweet.replace(emoji, "EMOJI" + emojis[emoji])        
        # Replace @USERNAME to 'USER'.
        tweet = re.sub(userPattern,' USER', tweet)        
        # Replace all non alphabets.
        tweet = re.sub(alphaPattern, " ", tweet)
        # Replace 3 or more consecutive letters by 2 letter.
        tweet = re.sub(sequencePattern, seqReplacePattern, tweet)

        tweetwords = ''
        for word in tweet.split():
            # Checking if the word is a stopword.
            #if word not in stopwordlist:
            if len(word)>1:
                # Lemmatizing the word.
                word = wordLemm.lemmatize(word)
                tweetwords += (word+' ')
            
        processedText.append(tweetwords)
        
    return processedText

def predict_image(img_path):
    classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
    img_size = (224 ,244)
    # batch_size = 16

    gambar = tf.keras.preprocessing.image.load_img(img_path, target_size=img_size)

    # Preprocessing the image

    # x = image.img_to_array(img)
    input_arr = tf.keras.preprocessing.image.img_to_array(gambar)
    input_arr = np.array([input_arr])
    predict = imageModel.predict(input_arr)
    predicted_class = np.argmax(predict, axis=-1)
    confidence_score = predict[0][predicted_class]

    preds = [classes[i] for i in predicted_class]
    return preds

def predict_text(vectoriser, model, text):
    # Predict the sentiment
    textdata = vectoriser.transform(preprocess(text))
    sentiment = model.predict(textdata)
    
    # Make a list of text with sentiment.
    data = []
    for text, pred in zip(text, sentiment):
        data.append((text,pred))
        
    # Convert the list into a Pandas DataFrame.
    df = pd.DataFrame(data, columns = ['text','sentiment'])
    df = df.replace([0,1,2,3], ['Glioma','Meningioma', 'Pituitary', 'No Tumor'])
    return df.head()['sentiment'][0]

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('./index.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files.get("imageOne")
        textToPredict = [request.form.get('desc')]

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        imageResult = predict_image(file_path)
        textResult = predict_text(vectoriser, LRmodel, textToPredict)

        dataImage = textImage = readMoreImage = dataText = textText = readMoreText = None

        if imageResult[0] == 'glioma':
            dataImage = "According to your brain MRI scan, you got Glioma tumor type. Glioma is a type of tumor that originates from glial cells in the brain or spinal cord. Glial cells are support cells that help maintain the health and normal functioning of nerve cells in the central nervous system."
            textImage = 'Read more about glioma tumor type...'
            readMoreImage = 'https://braintumourresearch.org/blogs/types-of-brain-tumour/glioma'
        elif imageResult[0] == 'meningioma':
            dataImage = "According to your brain MRI scan, you got Meningioma tumor type. A meningioma tumor is a type of tumor that develops from the meninges, which are the protective layers covering the brain and spinal cord. These tumors are typically slow-growing and often benign (non-cancerous). Meningiomas originate from cells of the meninges and can occur in various parts of the brain."
            textImage = 'Read more about meningioma tumor type...'
            readMoreImage = 'https://braintumourresearch.org/blogs/types-of-brain-tumour/meningioma'
        elif imageResult[0] == 'pituitary':
            dataImage = "According to your brain MRI scan, you got Pituitary. A pituitary tumor is a type of growth that forms in the pituitary gland, a small pea-sized gland located at the base of the brain. The pituitary gland plays a crucial role in regulating various hormones that control many functions in the body."
            textImage = 'Read more about pituitary tumor type...'
            readMoreImage = 'https://nyulangone.org/conditions/pituitary-tumors/types'
        elif imageResult[0] == 'notumor':
            dataImage = "Congratulation! You are free from brain tumor :D But, you still have to maintain your health."
            textImage = 'Read more about how to maintain your health...'
            readMoreImage = 'https://www.bannerhealth.com/services/cancer/cancer-type/brain-cancer/risk-factors-and-prevention'

        if textResult == 'Glioma':
            dataText = "According to your description of your health condition right now, you got Glioma tumor type. Glioma is a type of tumor that originates from glial cells in the brain or spinal cord. Glial cells are support cells that help maintain the health and normal functioning of nerve cells in the central nervous system."
            textText = 'Read more about glioma tumor type...'
            readMoreText = 'https://braintumourresearch.org/blogs/types-of-brain-tumour/glioma'
        elif textResult == 'Meningioma':
            dataText = "According to your description of your health condition right now, you got Meningioma tumor type. A meningioma tumor is a type of tumor that develops from the meninges, which are the protective layers covering the brain and spinal cord. These tumors are typically slow-growing and often benign (non-cancerous). Meningiomas originate from cells of the meninges and can occur in various parts of the brain."
            textText = 'Read more about meningioma tumor type...'
            readMoreText = 'https://braintumourresearch.org/blogs/types-of-brain-tumour/meningioma'
        elif textResult == 'Pituitary':
            dataText = "According to your description of your health condition right now, you got Pituitary. A pituitary tumor is a type of growth that forms in the pituitary gland, a small pea-sized gland located at the base of the brain. The pituitary gland plays a crucial role in regulating various hormones that control many functions in the body."
            textText = 'Read more about pituitary tumor type...'
            readMoreText = 'https://nyulangone.org/conditions/pituitary-tumors/types'
        elif textResult == 'No Tumor':
            dataText = "Congratulation! You are free from brain tumor :D But, you still have to maintain your health."
            textText = 'Read more about how to maintain your health...'
            readMoreText = 'https://www.bannerhealth.com/services/cancer/cancer-type/brain-cancer/risk-factors-and-prevention'

        data = [dataImage, textImage, readMoreImage, dataText, textText, readMoreText]

        return data
    
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=True)