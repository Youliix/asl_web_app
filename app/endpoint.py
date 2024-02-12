import pandas as pd
import joblib
import numpy as np

from flask import render_template, request, jsonify, make_response, Blueprint

from .db import save_image_content

endpoint = Blueprint('endpoint', __name__)

model = joblib.load('app/static/src/model/model_xgb_xyz_angles_v1.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
joint_list = [[4,3,2], [8,7,6], [12,11,10], [16,15,14], [20,19,18]]

@endpoint.route('/')
def home():
    return render_template('index.html')


@endpoint.route('/predict', methods=['POST'])
def predict():
    try:
        keypoints = request.form['keypoints']   
        keypoints = eval(keypoints)
        keypoints = [coord for point in keypoints for coord in point.values()]
        keypoints_angles = draw_finger_angles(keypoints, joint_list)
        prediction = predict_class(keypoints, keypoints_angles)
        img = request.files['image']
        save_content(img, keypoints, prediction)
    except Exception as e:
        return make_response(jsonify({'error': e}), 500)
    finally:
        return jsonify({'letter': prediction})


def predict_class(keypoints, keypoints_angles):
    df = pd.DataFrame([keypoints, keypoints_angles])
    print(df.head())
    prediction = model.predict(df)
    prediction = class_names[prediction[0]]
    return prediction


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)


def draw_finger_angles(keypoints, joint_list):
    list_angles = []
    for joint in joint_list:
        a = keypoints[joint[0]]
        b = keypoints[joint[1]]
        c = keypoints[joint[2]]
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle
        list_angles.append(angle)
    return list_angles
