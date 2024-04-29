// static/matchmaking/js/matchmaking.js
document.addEventListener('DOMContentLoaded', function() {
    const matchStatus = document.getElementById('match-status');
    const queueBtn = document.getElementById('queue-btn');

    const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsPath = wsScheme + window.location.host + '/ws/matchmaking/';
    const socket = new WebSocket(wsPath);

    socket.onopen = function(event) {
        console.log('WebSocket connected');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        matchStatus.innerHTML = data.message;
    };

    queueBtn.onclick = function() {
        socket.send(JSON.stringify({
            'action': 'queue_for_match'
        }));
    };
});
