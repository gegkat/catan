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
        vertex = { x: hexagon.center[0], y: hexagon.center[1], radius: 15, color: '#FFDAB9' }
        drawVertex(ctx, vertex);
        drawText(ctx, hexagon.number.toString(), hexagon.center[0], hexagon.center[1], '20px Arial', 'black');
    }
}

function drawVertex(ctx, vertex) {
    console.log('drawVertex', vertex)
    ctx.beginPath();
    ctx.arc(vertex.x, vertex.y, vertex.radius, 0, 2 * Math.PI);
    ctx.fillStyle = vertex.color;
    ctx.fill();
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
