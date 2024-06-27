import flask
import hexagon
import copy

class State:
    def __init__(self) -> None:
        self.hexagons = []
        self.vertices = []
        self.history = []
        self.future = []

    def copy_state(self) -> tuple[list[hexagon.Hexagon], list[hexagon.Vertex]]:
        return copy.deepcopy((self.hexagons, self.vertices))

    def save_state(self) -> None:
        self.history.append(self.copy_state())
        self.future.clear()  # Clear the future stack whenever a new state is saved

    def reset(self) -> None:
        self.hexagons = []
        self.vertices = []

    def update_vertices(self) -> None:
        vertex_set = set()
        for hex in self.hexagons:
            for vertex in hex.get_vertices_coordinates():
                vertex_set.add(vertex)

        vertices = list(vertex_set)
        for vertex in vertices:
            self.vertices.append(hexagon.Vertex(vertex))

    def update_hexagons(self, hexagons: list[hexagon.Hexagon]) -> None:
        '''Configures a hexagonal tiling.'''
        self.save_state()
        self.reset()
        self.hexagons = hexagons
        self.update_vertices()

    def handle_click(self, click_pixel: hexagon.Pixel) -> None:
        # Check if a vertex was clicked
        for vertex in self.vertices:
            if vertex.inside(click_pixel):
                self.save_state()
                vertex.toggle_color()
                return 

        # Check if a hexagon was clicked
        for hex in self.hexagons:
            if hex.inside(click_pixel):
                self.save_state()
                hex.toggle_color()
                return 
        
    def back(self) -> None:
        if self.history:
            self.future.append(self.copy_state())
            self.hexagons, self.vertices = self.history.pop()

    def forward(self) -> None:
        if self.future:
            self.history.append(self.copy_state())
            self.hexagons, self.vertices = self.future.pop()

    def get_json(self) -> flask.Response:
        hexagon_dicts = [hex.to_dict() for hex in self.hexagons]
        vertices_dicts = [v.to_dict() for v in self.vertices]
        return flask.jsonify(hexagons=hexagon_dicts, vertices=vertices_dicts)