import pandas as pd
import joblib
import numpy as np
import logging

from .db import save_image_content

model = joblib.load("app/static/src/model/work/models/model_xgb.pkl")


class_names = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
]


def predict_class_from_features(features):
    keypoints = features["keypoints"]
    angles = features["angles"]
    distances = features["distances"]
    angles_dict = {f"angle_{i}": value for i, value in enumerate(angles)}
    distances_dict = {f"dist_{i}": value for i, value in enumerate(distances)}
    data = {**keypoints, **angles_dict, **distances_dict}
    s = pd.DataFrame([data])
    prediction = model.predict(s)
    result = class_names[prediction[0]]
    return result


def calculate_features_from_wrist(hand_landmarks):
    wrist = np.array([hand_landmarks[0]["x"], hand_landmarks[0]["y"]])
    angles = []
    distances = []
    
    for i in range(1, len(hand_landmarks)):
        keypoint = np.array([hand_landmarks[i]["x"], hand_landmarks[i]["y"]])
    
        vector_2d = keypoint[:2] - wrist[:2]
        angle_rad = np.arctan2(vector_2d[1], vector_2d[0])
        angle_deg = np.degrees(angle_rad)
        angles.append(angle_deg)

        distance = np.linalg.norm(keypoint - wrist)
        distances.append(distance)

    specific_keypoints_pairs = [
        (4, 8),
        (8, 12),
        (12, 16),
        (16, 20),
        (4, 17),
    ]
    for pair in specific_keypoints_pairs:
        point_a = np.array([hand_landmarks[pair[0]]["x"], hand_landmarks[pair[0]]["y"]])
        point_b = np.array([hand_landmarks[pair[1]]["x"], hand_landmarks[pair[1]]["y"]])
        specific_distance = np.linalg.norm(point_a - point_b)
        distances.append(specific_distance)

    keypoint_indices = [0, 4, 8, 12, 16, 20]
    keypoints_features = {}
    for index, hand in enumerate(hand_landmarks):
        if index in keypoint_indices:
            keypoints_features[f"x_{index}"] = hand["x"]
            keypoints_features[f"y_{index}"] = hand["y"]
    keypoints = keypoints_features

    return {"angles": angles, "distances": distances, "keypoints": keypoints}


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)
