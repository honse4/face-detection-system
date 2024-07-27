const video = document.getElementById('video');
const canvas = document.createElement('canvas');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const messageDiv = document.getElementById('message')


let captureInterval;
let sendInterval;
let framesBatch = [];
let stream;

canvas.width = 320;
canvas.height = 240;

let constraints = {
     video: true
};

navigator.mediaDevices.enumerateDevices()
            .then(function(devices) {
                const videoSelect = document.getElementById('cameraSelect');
                devices.forEach(function(device) {
                    if (device.kind === 'videoinput') {
                        const option = document.createElement('option');
                        option.value = device.deviceId;
                        option.text = device.label || `Camera ${videoSelect.length + 1}`;
                        videoSelect.appendChild(option);
                    }
                });
            })
            .catch(function(err) {
                console.log(err.name + ": " + err.message);
            });

document.getElementById('cameraSelect').addEventListener('change', function() {
    const deviceId = this.value;
    constraints = {
        video: {
             deviceId: { exact: deviceId }
        }
    };
    startStream();
});

function startStream() {
    if (stream) {
        stopStream();
    }
            
    navigator.mediaDevices.getUserMedia(constraints)
    .then(s => {
            stream = s;
                video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing the webcam:', error);
    });
}
            
function stopStream() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}         


startButton.addEventListener('click',async () => {
    startButton.disabled = true;
    stopButton.disabled = false;

    await loadModels();
    startStream();

    captureInterval = setInterval(captureFrame, 1000 / 3); 
    sendInterval = setInterval(sendFramesBatch, 3000); 
});

stopButton.addEventListener('click', () => {
    clearInterval(captureInterval);
    clearInterval(sendInterval);
    startButton.disabled = false;
    stopButton.disabled = true;

    stopStream();
});

async function loadModels() {
    await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');
}

async function captureFrame() {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frameData = canvas.toDataURL('image/jpeg', 0.5); 
    const image = await faceapi.fetchImage(frameData);

    const detections = await faceapi.detectAllFaces(image, new faceapi.TinyFaceDetectorOptions());

    if (detections.length > 0) {
        framesBatch.push(frameData);
    }
}

async function sendFramesBatch() {
    if (framesBatch.length > 0) {
        const compressedData = pako.deflate(JSON.stringify(framesBatch));
        framesBatch = [];

        try {
            console.log("Computed")
            const response = await fetch('/upload-frames', {
                method: 'POST',
                headers: {
                            'Content-Type': 'application/octet-stream'
                },
                    body: compressedData
            })
            if (response.ok) {
                const result = await response.json();
                console.log(result);
                if(result != null) {
                    displayMatch(result)
                }          
            } else {
                console.error('Server responded with an error:', response.statusText);
            }
        }
        
        catch (error) {
            console.error('Error sending frames to server:', error);
        }
    }
}

function displayMatch(name) {
    const nametag = document.createElement('div');
    nametag.textContent = 'Present: ' + name;
    nametag.classList.add('message');
    messageDiv.appendChild(nametag);

    setTimeout(() => {
        messageDiv.removeChild(nametag);
    }, 3000);
}