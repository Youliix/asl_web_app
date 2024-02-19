from flask import render_template, request, jsonify, make_response, Blueprint
from .detect import calculate_features_from_wrist, predict_class_from_features, save_content

endpoint = Blueprint('endpoint', __name__)

@endpoint.route('/')
def home():
    main_template = './content/home.html'
    return render_template('index.html', main_template=main_template)

@endpoint.route('/predict', methods=['GET'])
def get_predict():
    main_template = './content/detection.html'
    return render_template('index.html', main_template=main_template)

@endpoint.route('/predict', methods=['POST'])
def post_predict():
    try:
        keypoints = request.form['keypoints']   
        keypoints = eval(keypoints)
        keypoints_features = calculate_features_from_wrist(keypoints)
        prediction = predict_class_from_features(keypoints_features)
        img = request.files['image']
        save_content(img, keypoints, prediction)
    except Exception as e:
        return make_response(jsonify({'error': e}), 500)
    finally:
        return jsonify({'letter': prediction})
