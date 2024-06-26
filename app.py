from flask import Flask, render_template, request, jsonify
from math import cos, sin, pi, sqrt
from dataclasses import dataclass

app = Flask(__name__)

VERTEX_RADIUS = 10
START_X = 800
START_Y = 300
HEXAGON_SIZE = 50
HEXAGON_COLORS = ("orange", "red")
VERTEX_COLORS = ("blue", "green")


def deg2rad(x):
    return pi / 180 * x

@dataclass(frozen=True, eq=True)
class Pixel: 
    x: float
    y: float

    def distance(self, other): 
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx*dx + dy*dy)

@dataclass(frozen=True, eq=True)
class Coordinate:
    q: int
    r: int
    s: int

    def to_pixel(self):
        dx = (self.q - self.s) * sqrt(3) / 2
        dy = self.r - (self.q + self.s) / 2
        x = START_X + HEXAGON_SIZE * dx
        y = START_Y + HEXAGON_SIZE * dy
        return Pixel(x, y)
    
    def add(self, dq, dr, ds):
        return Coordinate(self.q + dq, self.r + dr, self.s + ds)

class Hexagon: 
    def __init__(self, q, r):
        self.coordinate = Coordinate(q, r, -q - r)
        self.color_index = 0

    def get_pixel(self):
        return self.coordinate.to_pixel()

    def get_vertices_coordinates(self):
        # clockwise starting with +q
        return (
            self.coordinate.add( 1,  0,  0),
            self.coordinate.add( 0,  0, -1),
            self.coordinate.add( 0,  1,  0),
            self.coordinate.add(-1,  0,  0),
            self.coordinate.add( 0,  0,  1),
            self.coordinate.add( 0, -1,  0),
        )
    
    # This is approximate. This checks if we are inside the inner circle.
    def inside(self, pixel):
        return pixel.distance(self.get_pixel()) < HEXAGON_SIZE * sqrt(3) / 2

    def toggle_color(self):
        print(self.coordinate)
        self.color_index += 1

    def color(self):
        return HEXAGON_COLORS[self.color_index % len(HEXAGON_COLORS)]
    
    def to_dict(self):
        pixels = [c.to_pixel() for c in self.get_vertices_coordinates()]
        return {'vertices':[(p.x, p.y) for p in pixels], 
                'color': self.color()}

    
class Vertex: 
    def __init__(self, coordinate):
        self.coordinate = coordinate
        self.color_index = 0

    def get_pixel(self):
        return self.coordinate.to_pixel()
    
    def inside(self, pixel):
        return pixel.distance(self.get_pixel()) < VERTEX_RADIUS

    def toggle_color(self):
        print(self.coordinate)
        self.color_index += 1

    def color(self):
        return VERTEX_COLORS[self.color_index % len(VERTEX_COLORS)]
    
    def to_dict(self):
        pixel = self.get_pixel()
        return {'x': pixel.x, 'y': pixel.y, 'radius': VERTEX_RADIUS, 'color': self.color()}

class State:
    def __init__(self):
        self.hexagons = []
        self.vertices = []
    
    def calculate_hexagon_positions(self):
        vertex_set = set()

        # Central hexagon
        N = 10
        for i in range(-N, N):
            for j in range(-N, N):
                self.hexagons.append(Hexagon(i, j))

        for hex in self.hexagons:
            for vertex in hex.get_vertices_coordinates():
                vertex_set.add(vertex)

        vertices = list(vertex_set)
        for vertex in vertices:
            self.vertices.append(Vertex(vertex))

    def handle_click(self, click_pixel):
        # Check if a vertex was clicked
        for vertex in self.vertices:
            if vertex.inside(click_pixel):
                vertex.toggle_color()
                return 

        # Check if a hexagon was clicked
        for hex in self.hexagons:
            if hex.inside(click_pixel):
                hex.toggle_color()
                return 
        
    def get_json(self):
        hexagon_dicts = [hex.to_dict() for hex in self.hexagons]
        vertices_dicts = [v.to_dict() for v in self.vertices]
        return jsonify(hexagons=hexagon_dicts, vertices=vertices_dicts)
    
state = State()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    state.calculate_hexagon_positions()
    return state.get_json()

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.json
    state.handle_click(Pixel(data['x'], data['y']))
    return state.get_json()

if __name__ == '__main__':
    app.run(debug=True)
