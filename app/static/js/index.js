import { FilesetResolver, HandLandmarker } from 'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.9/+esm';

let BASE_URL = 'https://asl-web-app.onrender.com';
let handLandmarker;
let runningMode = 'VIDEO';
let predictedLetter = '';
const spinner = document.querySelector('.fa-spinner');

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
  enableWebcam();
};
createHandLandmarker();

let webcamRunning = false;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const canvasCtx = canvas.getContext('2d');

const adjustCanvasSize = () => {  
  if (video.videoWidth > 0 && video.videoHeight > 0) {
    const aspectRatio = video.videoWidth / video.videoHeight;
    const displayWidth = video.offsetWidth;
    const displayHeight = displayWidth / aspectRatio;
    canvas.width = displayWidth;
    canvas.height = displayHeight;
  }
  console.log('Canvas size:', canvas.width, canvas.height);
};

window.addEventListener('resize', adjustCanvasSize);

const enableWebcam = async () => {
  webcamRunning = true;

  const constraints = {
    video: true
  };

  await navigator.mediaDevices.getUserMedia(constraints).then((stream) => {
    video.srcObject = stream;
    video.addEventListener("loadeddata", () => {
      if (video.readyState >= 3) {
        spinner.style.display = 'none';
      }
      adjustCanvasSize();
      predictWebcam();
    });
  });
};

const drawBoundingBox = (keypoints) => {
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  for (let i = 0; i < keypoints.length; i++) {
    const x = keypoints[i].x * canvas.width;
    const y = keypoints[i].y * canvas.height;
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);
    minY = Math.min(minY, y);
    maxY = Math.max(maxY, y);
  }

  canvasCtx.strokeStyle = 'green';
  canvasCtx.lineWidth = 4;
  canvasCtx.strokeRect(minX, minY, maxX - minX, maxY - minY);
  if (predictedLetter) {
    canvasCtx.font = '18px Arial';
    canvasCtx.fillStyle = 'yellow';
    const textWidth = canvasCtx.measureText(predictedLetter).width;
    canvasCtx.fillText(predictedLetter, maxX - textWidth, minY);
  }
}

const drawHandKeypoints = (keypoints) => {
  canvasCtx.fillStyle = "blue"; 
  for (let i = 0; i < keypoints.length; i++) {
    const x = keypoints[i].x * canvas.width;
    const y = keypoints[i].y * canvas.height;
    canvasCtx.beginPath();
    canvasCtx.arc(x, y, 5, 0, 2 * Math.PI);
    canvasCtx.fill();
  }
  drawBoundingBox(keypoints);
}

let lastVideoTime = -1;
let results = undefined;

const predictWebcam = async () => {

  let startTimeMs = performance.now();
  if (lastVideoTime !== video.currentTime) {
    lastVideoTime = video.currentTime;
    results = await handLandmarker.detectForVideo(video, startTimeMs);
  }

  if (results && results.landmarks && results.landmarks.length > 0) {
    const dataUrl = canvas.toDataURL("image/jpeg", 1.0);
    const keypoints = results.landmarks[0];
    const prediction = await sendKeypointsToBackend(keypoints, dataUrl);
    
    if (prediction && prediction.letter) {
      // canvasCtx.save();
      predictedLetter = prediction.letter;
      drawHandKeypoints(keypoints);
      // canvasCtx.restore();
    }

  }
  if (webcamRunning === true) {
    window.requestAnimationFrame(predictWebcam);
    context.clearRect(0, 0, canvas.width, canvas.height);
  }
}

const sendKeypointsToBackend = async (keypoints, dataUrl) => {
  
  const formData = new FormData();  
  const blob = new Blob([JSON.stringify(dataUrl)], { type: "image/jpeg" });

  formData.append('keypoints', JSON.stringify(keypoints));
  formData.append('image', blob, 'image.jpg');

  try {
    // const response = await fetch(BASE_URL + '/predict', {
      const response = await fetch('/predict', {
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
