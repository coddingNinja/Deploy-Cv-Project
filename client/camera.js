const video = document.getElementById('video');
const handBox = document.getElementById('hand');
const cardsBox = document.getElementById('cards');

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
})
.catch(err => console.error("Error accessing camera:", err));

// Send video frame every 1 sec
setInterval(async () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/jpeg');

    const res = await fetch('/detect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image: dataURL})
    });
    const result = await res.json();
    handBox.innerText = result.hand;
    cardsBox.innerText = result.cards.join(', ');
}, 1000);

// Upload image detection
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadHand = document.getElementById('uploadHand');
const uploadCards = document.getElementById('uploadCards');

uploadBtn.addEventListener('click', async () => {
    if(fileInput.files.length === 0) return alert("Select an image");
    const file = fileInput.files[0];
    const reader = new FileReader();
    reader.onload = async () => {
        const res = await fetch('/detect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({image: reader.result})
        });
        const result = await res.json();
        uploadHand.innerText = result.hand;
        uploadCards.innerText = result.cards.join(', ');
    };
    reader.readAsDataURL(file);
});
