const video = document.getElementById('video');
const canvas = document.createElement('canvas');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const attButton = document.getElementById('attendance-button')
const buttonDiv = document.getElementById('button-div')
const vidDiv = document.getElementById('video-recording')

var attendance = false

let captureInterval;
let sendInterval;
let framesBatch = [];
let stream;

canvas.width = 320;
canvas.height = 240;

const constraints = {
     video: true
};

attButton.addEventListener('click', () => {
    attendance = true
    buttonDiv.removeChild(attButton)
    vidDiv.style.display = 'flex'
    
})

startButton.addEventListener('click', () => {
    startButton.disabled = true;
    stopButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints)
    .then(s => {
        stream = s
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing the webcam:', error);
    });

    captureInterval = setInterval(captureFrame, 1000 / 10); 
    sendInterval = setInterval(sendFramesBatch, 5000); 
});

stopButton.addEventListener('click', () => {
    clearInterval(captureInterval);
    clearInterval(sendInterval);
    startButton.disabled = false;
    stopButton.disabled = true;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});

function captureFrame() {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frameData = canvas.toDataURL('image/jpeg', 0.5); 
    framesBatch.push(frameData);

}

function sendFramesBatch() {
    if (framesBatch.length > 0) {
        const compressedData = pako.deflate(JSON.stringify(framesBatch));
        framesBatch = [];

        fetch('/upload-frames', {
            method: 'POST',
            headers: {
                        'Content-Type': 'application/octet-stream'
            },
                body: compressedData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Batch sent successfully:', data);
        })
        .catch(error => {
            console.error('Error sending frames batch to the server:', error);
        });
    }
}