import pandas as pd
import joblib

from flask import Flask, render_template, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model = joblib.load('./static/src/model/sklearn_xgb_v1.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)
    
    for point in data['keypoints']:
        del point['z']

    data['keypoints'] = [coord for point in data['keypoints'] for coord in point.values()]
    df = pd.DataFrame([data['keypoints']])
    prediction = model.predict(df)
    prediction = class_names[prediction[0]]
    
    return jsonify({'letter': prediction})

if __name__ == '__main__':
    app.run(debug=True)
