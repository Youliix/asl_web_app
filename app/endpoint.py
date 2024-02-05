import pandas as pd
import joblib

from flask import render_template, request, jsonify, make_response, Blueprint

endpoint = Blueprint('endpoint', __name__)

# model = joblib.load('./static/src/model/sklearn_xgb_v1.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']


@endpoint.route('/')
def home():
    return render_template('index.html')


@endpoint.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)
    
    for point in data['keypoints']:
        del point['z']

    data['keypoints'] = [coord for point in data['keypoints'] for coord in point.values()]
    df = pd.DataFrame([data['keypoints']])
    # prediction = model.predict(df)
    # prediction = class_names[prediction[0]]
    
    return jsonify({'letter': 'prediction'})


@endpoint.route('/save_content', methods=['POST'])
def save_content():
    data = request.get_json()
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)
    
    with open('./static/src/letter/' + data['letter'] + '.txt', 'w') as file:
        file.write(data['content'])
    
    return jsonify({'message': 'Content saved successfully!'})