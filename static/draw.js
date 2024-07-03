const radiusMap = {
    2: 13,  // Same value for 2 and 12
    3: 18, // Same value for 3 and 11
    4: 20, // Same value for 4 and 10
    5: 22, // Same value for 5 and 9
    6: 30, // Same value for 6 and 8
};

function getRadius(x) {
    const key = Math.min(x, 14 - x);
    return radiusMap[key] || 0; // Return 0 or some default value if not in the map
}

function drawHexagon(ctx, hexagon) {
    ctx.beginPath();
    hexagon.vertices.forEach(([x, y], index) => {
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.closePath();
    ctx.fillStyle = hexagon.color;
    ctx.fill();
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw the number in the center if not 7
    if (hexagon.number !== 7) {
        vertex = {
            x: hexagon.center[0], y: hexagon.center[1],
            radius: getRadius(hexagon.number), color: '#FFDAB9',
            outline: true
        }
        drawVertex(ctx, vertex, true);
        drawText(ctx, hexagon.number.toString(), hexagon.center[0], hexagon.center[1], '20px Arial', 'black');
    }
}

function drawVertex(ctx, vertex) {
    console.log('drawVertex', vertex)
    ctx.beginPath();
    ctx.arc(vertex.x, vertex.y, vertex.radius, 0, 2 * Math.PI);
    ctx.fillStyle = vertex.color;
    ctx.fill();
    if (vertex.outline) {
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 1;  // You can adjust this value to change the outline thickness
        ctx.stroke();
    }
}

function drawLine(ctx, line) {
    ctx.beginPath();
    ctx.moveTo(line.x1, line.y1);
    ctx.lineTo(line.x2, line.y2);
    ctx.lineTo(line.x3, line.y3);
    ctx.lineTo(line.x4, line.y4);
    ctx.closePath();
    ctx.fillStyle = line.color;
    ctx.fill();
}

function drawText(ctx, text, x, y, font, color) {
    ctx.fillStyle = color;
    ctx.font = font;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
}
