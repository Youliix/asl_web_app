import logging
import pandas as pd
import joblib
import numpy as np

from flask import render_template, request, jsonify, make_response, Blueprint

from .db import save_image_content

endpoint = Blueprint('endpoint', __name__)

model = joblib.load('app/static/src/model/work/model_xgb_xyz_angles_dist_xy.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

@endpoint.route('/')
def home():
    return render_template('index.html')


@endpoint.route('/predict', methods=['POST'])
def predict():
    try:
        keypoints = request.form['keypoints']   
        keypoints = eval(keypoints)
        keypoints_features = calculate_features_from_wrist(keypoints)
        prediction = predict_class(keypoints_features)
        # img = request.files['image']
        # save_content(img, keypoints, prediction)
    except Exception as e:
        return make_response(jsonify({'error': e}), 500)
    finally:
        return jsonify({'letter': prediction})


def predict_class(features):
    angles = features['angles']
    distances = features['distances']
    angle_dict = {f'angle_{i}': value for i, value in enumerate(angles)}
    distance_dict = {f'dist_{i}': value for i, value in enumerate(distances)}
    data = {**angle_dict, **distance_dict}
    s = pd.DataFrame([data])
    prediction = model.predict(s)
    result = class_names[prediction[0]]
    return result


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)


def calculate_features_from_wrist(hand_landmarks):
    wrist = np.array([hand_landmarks[0]['x'], hand_landmarks[0]['y']])
    angles = []
    distances = []

    for i in range(1, len(hand_landmarks)):  # Skip the wrist itself
        keypoint = np.array([hand_landmarks[i]['x'], hand_landmarks[i]['y']])
        
        # Calculate angle
        vector = keypoint - wrist
        angle_rad = np.arctan2(vector[1], vector[0])  # Angle in radians
        angle_deg = np.degrees(angle_rad)  # Convert to degrees
        angles.append(angle_deg)
        
        # Calculate distance
        distance = np.linalg.norm(vector)  # Euclidean distance
        distances.append(distance)
    # print(angles, distances)
        specific_keypoints_pairs = [(4, 8), (8, 12), (12, 16), (16, 20), (4,17), (3, 5), (4,20), (4,12), (4,16)]
    for pair in specific_keypoints_pairs:
        point_a = np.array([hand_landmarks[pair[0]]['x'], hand_landmarks[pair[0]]['y']])
        point_b = np.array([hand_landmarks[pair[1]]['x'], hand_landmarks[pair[1]]['y']])
        specific_distance = np.linalg.norm(point_a - point_b)
        # Append the specific distance with a descriptive key
        distances.append(specific_distance)
    return {'angles': angles, 'distances': distances}

