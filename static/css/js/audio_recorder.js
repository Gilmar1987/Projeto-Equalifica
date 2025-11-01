// static/js/audio_recorder.js

export async function gravarAudio(socket, callback) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];

        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        
        mediaRecorder.onstop = async () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(blob);
            } else {
                console.error('WebSocket is not open. readyState: ' + socket.readyState);
            }

            stream.getTracks().forEach(t => t.stop());
            if (callback) {
                callback();
            }
        };

        mediaRecorder.start();
        
        setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }, 10000); // Grava por 10 segundos

    } catch (error) {
        console.error('Erro ao gravar áudio:', error);
        if (callback) {
            callback(error);
        }
    }
}