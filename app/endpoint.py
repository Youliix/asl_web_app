import logging
import pandas as pd
import joblib

from flask import render_template, request, jsonify, make_response, Blueprint

from .db import save_image_content

endpoint = Blueprint('endpoint', __name__)

model = joblib.load('app/static/src/model/model_v1.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


@endpoint.route('/')
def home():
    return render_template('index.html')


@endpoint.route('/predict', methods=['POST'])
def predict():
    try:
        keypoints = request.form['keypoints']    
        prediction = predict_class(keypoints)
        img = request.files['image']
        save_content(img, keypoints, prediction)
    except Exception as e:
        return make_response(jsonify({'error': e}), 500)
    finally:
        return jsonify({'letter': prediction})


def predict_class(keypoints):
    keypoints = eval(keypoints)
    for point in keypoints:
        del point['z']
    keypoints = [coord for point in keypoints for coord in point.values()]
    df = pd.DataFrame([keypoints])
    prediction = model.predict(df)
    prediction = class_names[prediction[0]]
    return prediction


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)
