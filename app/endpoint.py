import logging
import pandas as pd
import joblib
import numpy as np

from flask import render_template, request, jsonify, make_response, Blueprint

from .db import save_image_content

endpoint = Blueprint('endpoint', __name__)

model = joblib.load('app/static/src/model/work/model_xgb_xyz_angles_only_v1.pkl')

class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

# joint_list = [[4,3,2], [8,7,6], [12,11,10], [16,15,14], [20,19,18]]
joint_list = [[4,1], [8,5], [12,9], [16,13], [20,17]]

# column_names = [f"{dim}{i}" for i in range(1, 22) for dim in ['x', 'y', 'z']] + [f"angle{j}" for j in range(1, 6)]
column_angles = [f"angle_{j}" for j in range(0, 5)]


@endpoint.route('/')
def home():
    return render_template('index.html')


@endpoint.route('/predict', methods=['POST'])
def predict():
    try:
        keypoints = request.form['keypoints']   
        keypoints = eval(keypoints)
        keypoints_angles = draw_finger_angles_by_base_of_wrist(keypoints)
        prediction = predict_class(keypoints, keypoints_angles)
        # img = request.files['image']
        # save_content(img, keypoints, prediction)
    except Exception as e:
        return make_response(jsonify({'error': e}), 500)
    finally:
        return jsonify({'letter': prediction})


def predict_class(keypoints, keypoints_angles):
    for keypoint in keypoints:
        del keypoint['z']
    keypoints_indices = [0, 4, 8, 12, 16, 20]
    new_keypoints = [keypoints[i] for i in keypoints_indices]
    keypoints = [item for sublist in keypoints for item in sublist.values()]
    
    s = pd.Series(keypoints_angles , keypoints)
    # df = pd.DataFrame([keypoints])
    # new_column_names = {}
    # for i, index in enumerate(keypoints_indices):
    #     new_column_names[str(i)] = f'x_{index}'
    #     new_column_names[str(i+1)] = f'y_{index}'

    # df.rename(columns=new_column_names, inplace=True)
    # df = df.drop(columns=keypoints_indices)
    # for i, index in enumerate(keypoints_indices):
    #     df[f'x_{index}'] = df['keypoints'].apply(lambda x: x[i][0] if isinstance(x, list) and len(x) > i and isinstance(x[i], tuple) else None)
    #     df[f'y_{index}'] = df['keypoints'].apply(lambda x: x[i][1] if isinstance(x, list) and len(x) > i and isinstance(x[i], tuple) else None)
    # df = df.drop(columns=['keypoints'])    
    # df = pd.DataFrame([keypoints_angles], columns=column_angles)
    # df = pd.concat([pd.DataFrame([keypoints_angles], columns=column_angles), df], axis=1)
    prediction = model.predict(s)
    result = class_names[prediction[0]]
    return result


def save_content(img, keypoints, prediction):
    save_image_content(img, keypoints, prediction)


# def draw_finger_angles(keypoints):
#     keypoints = eval(keypoints)
#     list_angles = []
#     for joint in joint_list:
#         a = keypoints[joint[0]]
#         b = keypoints[joint[1]]
#         c = keypoints[joint[2]]
#         radians = np.arctan2(c['y'] - b['y'], c['x'] - b['x']) - np.arctan2(a['y'] - b['y'], a['x'] - b['x'])
#         angle = np.abs(radians * 180.0 / np.pi)
#         if angle > 180.0:
#             angle = 360 - angle
#         list_angles.append(angle)
#     return list_angles


def draw_finger_angles_by_base_of_wrist(keypoints):
    angles = []
    for joint in joint_list:
        a = (keypoints[0]['x'], keypoints[0]['y'])
        b = (keypoints[joint[1]]['x'], keypoints[joint[1]]['y'])
        c = (keypoints[joint[0]]['x'], keypoints[joint[0]]['y'])
        angle = calculate_angle(a, b, c)
        angles.append(angle)
    return angles


def calculate_angle(a, b, c):
    a = np.array(a)  # Coordonnées du premier point
    b = np.array(b)  # Coordonnées du point de pivot
    c = np.array(c)  # Coordonnées du troisième point

    # Vecteurs de a à b et de c à b
    ab = a - b
    cb = c - b

    # Produit scalaire des vecteurs ab et cb
    dot_product = np.dot(ab, cb)

    # Normes (longueurs) des vecteurs ab et cb
    norm_ab = np.linalg.norm(ab)
    norm_cb = np.linalg.norm(cb)

    # Calcul de l'angle en radians entre les deux vecteurs
    angle = np.arccos(dot_product / (norm_ab * norm_cb))

    # Conversion de l'angle en degrés
    angle_deg = np.degrees(angle)

    return angle_deg