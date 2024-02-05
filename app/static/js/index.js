import { FilesetResolver, HandLandmarker } from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.9/+esm';

let handLandmarker;
let runningMode = 'VIDEO';

const createHandLandmarker = async () => {
  const vision = await FilesetResolver.forVisionTasks('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0/wasm');
  handLandmarker = await HandLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
      delegate: "GPU",
    },
    runningMode: runningMode,
    numHands: 1,
    minHandDetectionConfidence: 0.8,
    minTrackingConfidence: 0.8,
    minHandPresenceConfidence: 0.8
  });
};
createHandLandmarker();

let webcamRunning = false;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const canvasCtx = canvas.getContext('2d');
const predictedLetter = document.getElementById("predictedLetter");

const enableWebcam = async () => {
  webcamRunning = true;

  const constraints = {
    video: true
  };

  navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
    video.srcObject = stream;
    video.addEventListener("loadeddata", predictWebcam);
  });

};

enableWebcam();

let lastVideoTime = -1;
let results = undefined;

const predictWebcam = async () => {

  canvas.style.width = video.videoWidth;
  canvas.style.height = video.videoHeight;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  let startTimeMs = performance.now();
  if (lastVideoTime !== video.currentTime) {
    lastVideoTime = video.currentTime;
    results = await handLandmarker.detectForVideo(video, startTimeMs);
  }

  canvasCtx.save();
  
  if (results.landmarks.length > 0) {

    const dataUrl = canvas.toDataURL("image/jpeg", 1.0);
    const keypoints = results.landmarks[0];
    
    drawHandKeypoints(keypoints);

    const prediction = await sendKeypointsToBackend(keypoints, dataUrl);
    if (prediction && prediction.letter) {
      predictedLetter.innerHTML = prediction.letter;
    }
  }
  canvasCtx.restore();

  if (webcamRunning === true) {
    window.requestAnimationFrame(predictWebcam);
  }
}

const sendKeypointsToBackend = async (keypoints, dataUrl) => {
  
  const formData = new FormData();  
  const blob = new Blob([JSON.stringify(dataUrl)], { type: "image/jpeg" });

  formData.append('keypoints', JSON.stringify(keypoints));
  formData.append('image', blob, 'image.jpg');

  try {
    const response = await fetch('http://127.0.0.1:8000/predict', {
      method: 'POST',
      body: formData
    });
    if (!response.ok) {
      throw new Error('Error: ' + response.status);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.log('Erreur :', error);
  }
}

const drawHandKeypoints = (keypoints) => {
  for (let i = 0; i < keypoints.length; i++) {
    const x = keypoints[i].x * canvas.width;
    const y = keypoints[i].y * canvas.height;
    canvasCtx.beginPath();
    canvasCtx.arc(x, y, 5 /* rayon */, 0, 2 * Math.PI);
    canvasCtx.fillStyle = "red";
    canvasCtx.fill();
  }
}
