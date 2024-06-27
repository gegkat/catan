from flask import Flask, render_template, request, jsonify
from math import cos, sin, pi, sqrt
from dataclasses import dataclass
import os
import random
from enum import Enum
from typing import Any

app = Flask(__name__)

VERTEX_RADIUS = 8
START_X = 400
START_Y = 200
HEXAGON_SIZE = 30
VERTEX_COLORS = ("white", "blue", "green", "red", "yellow")

class Resource(Enum):
    DESERT = (0, '#F4A460') # (Sandy Brown)
    ORE = (1, '#7D7D7D') # (Dark Gray)
    SHEEP = (2, '#9ACD32') # (Yellow Green)
    WOOD = (3, '#228B22') # (Forest Green)
    BRICK = (4, '#B22222') # (Firebrick)
    WHEAT = (5, '#FFD700') # (Gold)

    def __init__(self, key: int, color: str) -> None:
        self.key = key
        self.color = color

    def next(self) -> 'Resource':
        members = list(self.__class__)
        index = (members.index(self) + 1) % len(members)
        return members[index]

def get_resources(num_resources: int) -> list[Resource]:
    ''' Generates a shuffled list of resources. Will include exactly 
    one desert and approximately equal amounts of the others.
    '''
    # Ensure we have exactly one desert
    resources = [Resource.DESERT]

    # Fill out list of resources in priority order.
    priority = (Resource.SHEEP, Resource.WOOD, Resource.WHEAT, 
             Resource.BRICK, Resource.ORE)
    for i in range(num_resources-1):
        resources.append(priority[i % len(priority)])

    random.shuffle(resources)
    return resources

def deg2rad(x: float) -> float:
    return pi / 180 * x

@dataclass(frozen=True, eq=True)
class Pixel: 
    x: float
    y: float

    def distance(self, other: 'Pixel') -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx*dx + dy*dy)

@dataclass(frozen=True, eq=True)
class Coordinate:
    q: int
    r: int
    s: int

    def to_pixel(self) -> Pixel:
        ''' We use cube coordinates here. 
        q points toward 2 on a clock.
        r points toward 6 on a clock.
        s points toward 10 on a clock.
        https://www.redblobgames.com/grids/hexagons/#coordinates-cube

        Since X points to 3 and Y points to 6, the x-y components of 
        each vector are:
        q: (cos(30), -sin(30))
        r: (0, 1)
        s: (-cos(30), -sin(30))
        '''
        dx = (self.q - self.s) * sqrt(3) / 2
        dy = self.r - (self.q + self.s) / 2
        x = START_X + HEXAGON_SIZE * dx
        y = START_Y + HEXAGON_SIZE * dy
        return Pixel(x, y)
    
    def add(self, dq: int, dr: int, ds: int) -> 'Coordinate':
        return Coordinate(self.q + dq, self.r + dr, self.s + ds)

class Hexagon: 
    def __init__(self, q: int, r: int, resource: Resource) -> None:
        self.coordinate = Coordinate(q, r, -q - r)
        self.resource = resource

    def get_pixel(self) -> Pixel:
        return self.coordinate.to_pixel()

    def get_vertices_coordinates(self) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate, Coordinate, Coordinate]:
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
    def inside(self, pixel: Pixel) -> bool:
        return pixel.distance(self.get_pixel()) < HEXAGON_SIZE * sqrt(3) / 2

    def toggle_color(self) -> None:
        self.resource = self.resource.next()

    def color(self) -> str:
        return self.resource.color
    
    def to_dict(self) -> dict:
        pixels = [c.to_pixel() for c in self.get_vertices_coordinates()]
        return {'vertices':[(p.x, p.y) for p in pixels], 
                'color': self.color()}

    
class Vertex: 
    def __init__(self, coordinate: Coordinate) -> None:
        self.coordinate = coordinate
        self.color_index = 0

    def get_pixel(self) -> Pixel:
        return self.coordinate.to_pixel()
    
    def inside(self, pixel: Pixel) -> bool:
        return pixel.distance(self.get_pixel()) < VERTEX_RADIUS

    def toggle_color(self) -> None:
        self.color_index += 1

    def color(self) -> str:
        return VERTEX_COLORS[self.color_index % len(VERTEX_COLORS)]
    
    def to_dict(self) -> dict[str, Any]:
        pixel = self.get_pixel()
        return {'x': pixel.x, 'y': pixel.y, 'radius': VERTEX_RADIUS, 'color': self.color()}

class State:
    def __init__(self) -> None:
        self.hexagons = []
        self.vertices = []

    def reset(self) -> None:
        self.__init__()
    
    def update_vertices(self) -> None:
        vertex_set = set()
        for hex in self.hexagons:
            for vertex in hex.get_vertices_coordinates():
                vertex_set.add(vertex)

        vertices = list(vertex_set)
        for vertex in vertices:
            self.vertices.append(Vertex(vertex))

    def hexagon_layout(self, num_rings: int) -> None:
        '''Configures a hexagonal tiling.'''
        N = num_rings
        self.__init__()
        num_hexagons = 1 + 3*(N-1)*N
        resources = get_resources(num_hexagons)
        for i in range(-N+1, N):
            for j in range(-N+1, N):
                if abs(i + j) >= N:
                    continue
                self.hexagons.append(Hexagon(i, j, resources.pop()))
        assert(len(resources) == 0)
        self.update_vertices()

    def diamond_layout(self, num_rings: int) -> None:
        '''Configures a diagonal tiling. '''
        N = num_rings
        self.__init__()
        num_hexagons = (2*N-1)**2
        resources = get_resources(num_hexagons)
        for i in range(-N+1, N):
            for j in range(-N+1, N):
                self.hexagons.append(Hexagon(i, j, resources.pop()))
        assert(len(resources) == 0)
        self.update_vertices()

    def handle_click(self, click_pixel: Pixel) -> None:
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
    
# Global state holds all info for the current game.
state = State()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    action = request.form.get('action')
    
    if action == 'hex':
        state.hexagon_layout(3)
    elif action == 'big_hex':
        state.hexagon_layout(4)
    elif action == 'diamond':
        state.diamond_layout(3)
    elif action == 'big_diamond':
        state.diamond_layout(4)

    return state.get_json()

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.json
    state.handle_click(Pixel(data['x'], data['y']))
    return state.get_json()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
