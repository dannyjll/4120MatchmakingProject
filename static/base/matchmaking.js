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
            var acceptbutton = document.createElement("button");
            acceptbutton.id = "accept-btn";
            acceptbutton.textContent = "Accept";
            var denybutton = document.createElement("button");
            denybutton.id = "deny-btn";
            denybutton.textContent = "Deny";
            var container = document.getElementById("acceptdeny");
            container.appendChild(acceptbutton);
            container.appendChild(denybutton);
            queueBtn.remove()
            document.getElementById('searching').innerHTML = "Match found!"
        }
    };

    queueBtn.onclick = function() {
        document.getElementById('searching').innerHTML = "You are now searching for a match!"
        const message = JSON.stringify({
        'action': 'queue_for_match'});
        console.log('Message:', message)
        socket.send(message)
    }
    acceptBtn.onclick = function() {
        const message = JSON.stringify({
        'action': ''});
        console.log('Message:', message)
        socket.send(message)
    }
    queueBtn.onclick = function() {
        document.getElementById('searching').innerHTML = "You are now searching for a match!"
        const message = JSON.stringify({
        'action': 'queue_for_match'});
        console.log('Message:', message)
        socket.send(message)
    }
});
