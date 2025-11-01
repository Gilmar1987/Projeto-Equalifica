// static/js/audio_recorder.js
// Variáveis globais
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let volumeMeter;

// Função para iniciar/parar gravação
async function gravarAudio(callback) {
    try {
        if (!isRecording) {
            // Inicia gravação
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            // Configura medidor de volume
            const audioContext = new AudioContext();
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            source.connect(analyser);
            
            // Atualiza medidor de volume
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            function updateVolume() {
                if (isRecording) {
                    analyser.getByteFrequencyData(dataArray);
                    const volume = Math.max(...dataArray) / 255;
                    const volumeBar = document.getElementById('volume-bar');
                    if (volumeBar) {
                        volumeBar.style.width = `${volume * 100}%`;
                        volumeBar.style.backgroundColor = volume > 0.75 ? 'red' : 'green';
                    }
                    requestAnimationFrame(updateVolume);
                }
            }

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                
                // Preview do áudio
                const audioUrl = URL.createObjectURL(audioBlob);
                const previewAudio = document.getElementById('audio-preview');
                if (previewAudio) {
                    previewAudio.src = audioUrl;
                }

                // Prepara FormData
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');

                try {
                    // Envia para transcrição
                    const response = await fetch('/accessibility/audio-to-libras/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    if (!response.ok) throw new Error('Erro na transcrição');

                    const data = await response.json();
                    callback(data.texto);
                } catch (error) {
                    console.error('Erro:', error);
                    callback('Erro na transcrição. Por favor, tente novamente.');
                }

                // Limpa recursos
                stream.getTracks().forEach(track => track.stop());
                URL.revokeObjectURL(audioUrl);
            };

            mediaRecorder.start(100); // Chunks a cada 100ms
            isRecording = true;
            updateVolume();
        } else {
            // Para gravação
            mediaRecorder.stop();
            isRecording = false;
        }
    } catch (error) {
        console.error('Erro ao acessar microfone:', error);
        callback('Erro ao acessar microfone. Verifique as permissões.');
    }
}