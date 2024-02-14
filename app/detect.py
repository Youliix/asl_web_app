
import pandas as pd
import joblib
import numpy as np

from .db import save_image_content

model = joblib.load('app/static/src/model/models/model_xgb_full_angles_5d_6p.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']


def predict_class(features):
    keypoints = features['keypoints']
    angles = features['angles']
    distances = features['distances']
    angle_dict = {f'angle_{i}': value for i, value in enumerate(angles)}
    distance_dict = {f'dist_{i}': value for i, value in enumerate(distances)}
    data = {**keypoints, **angle_dict, **distance_dict}
    s = pd.DataFrame([data])
    prediction = model.predict(s)
    result = class_names[prediction[0]]
    return result


def calculate_features_from_wrist(hand_landmarks):
    wrist = np.array([hand_landmarks[0]['x'], hand_landmarks[0]['y']])
    angles = []
    distances = []

    for i in range(1, len(hand_landmarks)):
        keypoint = np.array([hand_landmarks[i]['x'], hand_landmarks[i]['y']])
        
        vector = keypoint - wrist
        angle_rad = np.arctan2(vector[1], vector[0])
        angle_deg = np.degrees(angle_rad)
        angles.append(angle_deg)
        
        distance = np.linalg.norm(vector)
        distances.append(distance)
        specific_keypoints_pairs = [(4, 8), (8, 12), (12, 16), (16, 20), (4,17)]
    for pair in specific_keypoints_pairs:
        point_a = np.array([hand_landmarks[pair[0]]['x'], hand_landmarks[pair[0]]['y']])
        point_b = np.array([hand_landmarks[pair[1]]['x'], hand_landmarks[pair[1]]['y']])
        specific_distance = np.linalg.norm(point_a - point_b)
        distances.append(specific_distance)
    
    keypoint_indices = [0, 4, 8, 12, 16, 20]
    filtered_keypoints = {f'kp_{i}': hand_landmarks[i] for i in keypoint_indices if i < len(hand_landmarks)}
    for kp in filtered_keypoints.values():
        if 'z' in kp: del kp['z']

    keypoints_features = {}
    for i in keypoint_indices:
        kp_key = f'kp_{i}'
        if kp_key in filtered_keypoints:
            keypoints_features[f'x_{i}'] = filtered_keypoints[kp_key].get('x', None)
            keypoints_features[f'y_{i}'] = filtered_keypoints[kp_key].get('y', None)
    keypoints = keypoints_features

    return {'angles': angles, 'distances': distances, 'keypoints': keypoints}


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)
