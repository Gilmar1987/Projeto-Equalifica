// static/js/webrtc.js
let localStream;

export async function startMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        const video = document.getElementById('local-video');
        video.srcObject = localStream;
        video.play();
        return localStream;
    } catch (err) {
        alert("Permissão de câmera/microfone negada.");
        throw err;
    }
}

export function stopMedia() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
}