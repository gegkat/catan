import flask
import hexagon
import copy
import random

class Player:
    def __init__(self) -> None:
        self.resources = {
            'ore': 0,
            'wood': 0,
            'brick': 0,
            'wheat': 0,
            'sheep': 0,
        }
    
    def update_resource(self, resource: str, delta: int):
        self.resources[resource] = max(0, self.resources[resource] + delta)

class State:
    def __init__(self) -> None:
        self.reset()
        self.history = []
        self.future = []

    def roll_dice(self):
        self.save_state()
        self.dice = (random.randint(1, 6), random.randint(1, 6))

    def update_resource(self, resource: str, delta: int, color: str):
        self.save_state()
        self.players[color].update_resource(resource, delta)

    def copy_state(self) -> tuple[list[hexagon.Hexagon], list[hexagon.Vertex]]:
        return copy.deepcopy((self.hexagons, self.vertices, self.lines, self.players, self.dice))

    def save_state(self) -> None:
        self.history.append(self.copy_state())
        self.future.clear()  # Clear the future stack whenever a new state is saved

    def reset(self) -> None:
        self.hexagons = []
        self.vertices = []
        self.lines = []
        self.players = {'cyan': Player(), 
                        'magenta': Player(),
                        'purple': Player(),
                        'blue': Player(),
                        }
        self.dice = (0, 0)

    def get_neighbors(self, coord: hexagon.Coordinate) -> tuple[hexagon.Coordinate, hexagon.Coordinate, hexagon.Coordinate]:
        return (coord.add(1, 0, 1), coord.add(1, 1, 0), coord.add(0, 1, 1))

    def update_vertices(self) -> None:
        coord_set = set()
        for hex in self.hexagons:
            for coord in hex.get_vertices_coordinates():
                coord_set.add(coord)

        for coord in coord_set:
            self.vertices.append(hexagon.Vertex(coord))

        for coord in coord_set:
            for neighbor in self.get_neighbors(coord):
                if neighbor in coord_set and neighbor.greater(coord):
                    self.lines.append(hexagon.Line(coord, neighbor))

        # if len(self.lines) > 1:
        #     self.lines = [self.lines[0]]

    def update_hexagons(self, hexagons: list[hexagon.Hexagon]) -> None:
        '''Configures a hexagonal tiling.'''
        self.save_state()
        self.reset()
        self.hexagons = hexagons
        self.update_vertices()

    def handle_click(self, click_pixel: hexagon.Pixel, color: str) -> None:
        for vertex in self.vertices:
            if vertex.inside(click_pixel):
                print('Vertex: ', vertex.coordinate)
                self.save_state()
                vertex.toggle_color(color)
                return 

        for line in self.lines:
            if line.inside(click_pixel):
                self.save_state()
                line.toggle_color(color)
                return 
            
        # for hex in self.hexagons:
        #     if hex.inside(click_pixel):
        #         self.save_state()
        #         hex.toggle_color()
        #         return 
        
    def back(self) -> None:
        if self.history:
            self.future.append(self.copy_state())
            self.hexagons, self.vertices, self.lines, self.players, self.dice = self.history.pop()

    def forward(self) -> None:
        if self.future:
            self.history.append(self.copy_state())
            self.hexagons, self.vertices, self.lines, self.players, self.dice = self.future.pop()

    def serialize(self, socketio) -> flask.Response:
        hexagon_dicts = [hex.to_dict() for hex in self.hexagons]
        vertices_dicts = [v.to_dict() for v in self.vertices]
        lines_dicts = [l.to_dict() for l in self.lines]
        players_dicts = {c: p.resources for c, p in self.players.items()}
        state_as_dict = {'hexagons': hexagon_dicts, 
                         'vertices': vertices_dicts, 
                         'lines': lines_dicts,
                         'players': players_dicts,
                         'dice': self.dice}
        socketio.emit('state_update', state_as_dict)
        return flask.jsonify(state_as_dict)