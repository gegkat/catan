import flask
import hexagon
import board_layout
import state
import os

app = flask.Flask(__name__)
    
# Global state holds all info for the current game.
game_state = state.State()

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    action = flask.request.form.get('action')
    
    if action == 'hex':
        game_state.update_hexagons(board_layout.hexagon_layout(3))
    elif action == 'big_hex':
        game_state.update_hexagons(board_layout.hexagon_layout(4))
    elif action == 'diamond':
        game_state.update_hexagons(board_layout.diamond_layout(3))
    elif action == 'big_diamond':
        game_state.update_hexagons(board_layout.diamond_layout(4))

    return game_state.get_json()

@app.route('/click', methods=['POST'])
def handle_click():
    data = flask.request.json
    game_state.handle_click(hexagon.Pixel(data['x'], data['y']))
    return game_state.get_json()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
