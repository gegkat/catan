import flask
import flask_socketio
import hexagon
import board_layout
import state
import os
import eventlet
eventlet.monkey_patch()  # Make sure eventlet monkey patches for compatibility


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*")

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
    elif action == 'back':
        game_state.back()
    elif action == 'forward':
        game_state.forward()

    return game_state.serialize(socketio)

@app.route('/click', methods=['POST'])
def handle_click():
    data = flask.request.json
    game_state.handle_click(hexagon.Pixel(data['x'], data['y']))

    return game_state.serialize(socketio)

@socketio.on('connect')
def handle_connect():
    return game_state.serialize(socketio)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode)
