from flask import Flask, render_template, request, jsonify
import hexagon
import board_layout
import os

app = Flask(__name__)

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
        state.update_hexagons(board_layout.hexagon_layout(3))
    elif action == 'big_hex':
        state.update_hexagons(board_layout.hexagon_layout(4))
    elif action == 'diamond':
        state.update_hexagons(board_layout.diamond_layout(3))
    elif action == 'big_diamond':
        state.update_hexagons(board_layout.diamond_layout(4))

    return state.get_json()

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.json
    state.handle_click(hexagon.Pixel(data['x'], data['y']))
    return state.get_json()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
