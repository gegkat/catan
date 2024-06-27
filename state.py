import flask
import hexagon
import board_layout

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
            self.vertices.append(hexagon.Vertex(vertex))

    def update_hexagons(self, hexagons: list[hexagon.Hexagon]) -> None:
        '''Configures a hexagonal tiling.'''
        self.__init__()
        self.hexagons = hexagons
        self.update_vertices()

    def handle_click(self, click_pixel: hexagon.Pixel) -> None:
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
        return flask.jsonify(hexagons=hexagon_dicts, vertices=vertices_dicts)