document.addEventListener('DOMContentLoaded', function() {
    const matchStatus = document.getElementById('match-status');
    const queueBtn = document.getElementById('queue-btn');
    const acceptBtn = document.getElementById('accept-btn');
    const denyBtn = document.getElementById('deny-btn');
    const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsPath = wsScheme + window.location.host + '/ws/matchmaking/';
    const socket = new WebSocket(wsPath);

    socket.onopen = function(event) {
        console.log('WebSocket connected');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.message) {
            matchStatus.innerHTML = data.message;
        }
        if (data.opponent_username) {
            matchStatus.innerHTML += '<br>Your opponent is: ' + data.opponent_username;
            var denybutton = document.getElementById("deny-btn");
            var acceptbutton = document.getElementById("accept-btn");
            acceptbutton.disabled = false
            denybutton.disabled = false
            document.getElementById('searching').innerHTML = "Match found!"
        }
    };

    queueBtn.onclick = function() {
        document.getElementById('searching').innerHTML = "You are now searching for a match!"
        const message = JSON.stringify({
        'action': 'queue_for_match'});
        console.log('Message:', message)
        socket.send(message)
        queueBtn.remove()
    }
    acceptBtn.onclick = function() {
        const message = JSON.stringify({
        'action': 'accept_match'});
        console.log('Message:', message)
        socket.send(message)
    }
    denyBtn.onclick = function() {
        const message = JSON.stringify({
        'action': 'deny_match'});
        console.log('Message:', message)
        socket.send(message)
    }
});
