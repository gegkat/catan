from flask import Flask, render_template, request, jsonify
from math import cos, sin, pi, sqrt

app = Flask(__name__)

def calculate_hexagon_points(center_x, center_y, size):
    points = []
    vertices = []
    for i in range(6):
        angle_deg = 60 * i + 30
        angle_rad = pi / 180 * angle_deg
        x = center_x + size * cos(angle_rad)
        y = center_y + size * sin(angle_rad)
        points.append((x, y))
        vertices.append((x, y))
    return points, vertices

def calculate_hexagon_positions():
    size = 50
    horizontal_spacing = size * 1.5

    hexagon_data = []
    vertex_set = set()  # To store unique vertices

    # Central hexagon
    hexagon_points, vertices = calculate_hexagon_points(200, 200, size)
    hexagon_data.append(hexagon_points)
    vertex_set.update(vertices)

    # Right hexagon sharing two vertices
    hexagon_points, vertices = calculate_hexagon_points(200 + horizontal_spacing, 200, size)
    hexagon_data.append(hexagon_points)
    vertex_set.update(vertices)

    return hexagon_data, list(vertex_set)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    hexagon_data, vertices = calculate_hexagon_positions()
    return jsonify(hexagon_data=hexagon_data, vertices=vertices)

if __name__ == '__main__':
    app.run(debug=True)
