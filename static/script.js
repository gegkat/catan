let data = { hexagons: [], vertices: [], lines: [], players: {} };
const socket = io();

socket.on('state_update', (newData) => {
    data = newData;
    draw();
});

document.addEventListener('DOMContentLoaded', function () {
    const colorSelect = document.getElementById('color-select');
    colorSelect.addEventListener('change', function () {
        draw();
    });
});

async function handleEvent(event, action = null) {
    event.preventDefault();
    const color = document.getElementById('color-select').value;
    let x = null, y = null;

    // Determine if the source is the canvas and get coordinates
    if (event.target.id === 'canvas') {
        const rect = event.target.getBoundingClientRect();
        x = event.clientX - rect.left;
        y = event.clientY - rect.top;
    }

    const body = JSON.stringify({
        action,
        color,
        x,
        y
    });

    const response = await fetch('/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body
    });
    data = await response.json();
    draw();
}

function draw() {
    console.log('Data received by draw:', data);

    const color = document.getElementById('color-select').value;

    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'gray';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    data.hexagons.forEach(hexagon => {
        drawHexagon(ctx, hexagon.center, hexagon.vertices, hexagon.color, hexagon.number);
    });

    data.lines.forEach(line => {
        drawLine(ctx, line.x1, line.y1, line.x2, line.y2,
            line.x3, line.y3, line.x4, line.y4,
            line.width, line.color)
    });

    data.vertices.forEach(vertex => {
        drawVertex(ctx, vertex.x, vertex.y, vertex.radius, vertex.color)
    });

    Object.entries(data.players[color].resources).forEach(([resource, value]) => {
        document.getElementById(resource).textContent = value;
    });

    document.getElementById('dice').textContent = `${data.dice[0]} ${data.dice[1]}`;
    document.getElementById('cyan').textContent = `${data.players.cyan.num_cards}`;
    document.getElementById('magenta').textContent = `${data.players.magenta.num_cards}`;
    document.getElementById('purple').textContent = `${data.players.purple.num_cards}`;
    document.getElementById('blue').textContent = `${data.players.blue.num_cards}`;
}

window.onload = () => {
    document.getElementById('canvas').addEventListener('click', (event) => handleEvent(event, 'click'));
};