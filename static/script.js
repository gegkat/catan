let data = { hexagons: [], vertices: [], lines: [], players: {} };
const socket = io();

// Handle incoming data updates via WebSocket
socket.on('state_update', (newData) => {
    data = newData;
    draw();
});

// Set up listeners after the document has loaded
document.addEventListener('DOMContentLoaded', function () {
    const colorSelect = document.getElementById('color-select');
    colorSelect.addEventListener('change', draw);
    setupButtonListeners();
    setupCanvasListener();
});

// Sets up event listeners for all buttons using event delegation
function setupButtonListeners() {
    document.body.addEventListener('click', function (event) {
        if (event.target.tagName === 'BUTTON') {
            const action = event.target.getAttribute('data-action');
            if (action) {
                handleEvent(event, action);
            }
        }
    });
}

// Set up the canvas click event listener
function setupCanvasListener() {
    const canvas = document.getElementById('canvas');
    canvas.addEventListener('click', function (event) {
        handleEvent(event, 'click');
    });
}

// General handler for all game actions
async function handleEvent(event, action) {
    event.preventDefault();
    const color = document.getElementById('color-select').value;
    let coords = getCanvasCoordinates(event);

    const body = JSON.stringify({
        action,
        color,
        x: coords.x,
        y: coords.y
    });

    const response = await fetch('/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    });
    data = await response.json();
    draw();
}

// Helper to extract coordinates if the canvas was clicked
function getCanvasCoordinates(event) {
    let x = null, y = null;
    if (event.target.id === 'canvas') {
        const rect = event.target.getBoundingClientRect();
        x = event.clientX - rect.left;
        y = event.clientY - rect.top;
    }
    return { x, y };
}

// Render function to update the canvas and display data
function draw() {
    console.log('Data received by draw:', data);
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'gray';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw game elements
    data.hexagons.forEach(hexagon => drawHexagon(ctx, hexagon));
    data.lines.forEach(line => drawLine(ctx, line));
    data.vertices.forEach(vertex => drawVertex(ctx, vertex));

    // Update UI components with game data
    updateUI();
}

// Updates UI elements outside the canvas based on the current game state
function updateUI() {
    const color = document.getElementById('color-select').value;
    Object.entries(data.players[color].resources).forEach(([resource, value]) => {
        document.getElementById(resource).textContent = value;
    });

    document.getElementById('dice').textContent = `${data.dice[0]} ${data.dice[1]}`;
    document.getElementById('cyan').textContent = `${data.players.cyan.num_cards}`;
    document.getElementById('magenta').textContent = `${data.players.magenta.num_cards}`;
    document.getElementById('purple').textContent = `${data.players.purple.num_cards}`;
    document.getElementById('blue').textContent = `${data.players.blue.num_cards}`;
}
