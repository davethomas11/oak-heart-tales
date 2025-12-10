# react.py
import json

from flask import Flask, send_from_directory, request, jsonify
import os
from json_loader import JsonLoader
from text_loader import TextLoader
import secrets
import time

from main import Game  # Adjust import if needed

app = Flask(__name__, static_folder="react-ui/build", static_url_path="")

# Simple in-memory session store
SESSIONS = {}


def create_game():
    tiles = JsonLoader().load("data/tileset.json")
    game = Game.new_random(size=8, tileset=tiles)
    game.ascii_tiles = False
    game.data_loader = JsonLoader()
    game.ascii_loader = TextLoader("data/rooms")
    game.load_configurations("data/enemies.json")
    return game


def get_game(sid):
    if sid in SESSIONS:
        return SESSIONS[sid]
    # Create new game if not found
    game = create_game()
    SESSIONS[sid] = game
    return game


@app.route("/api/state")
def api_state():
    sid = request.args.get("sid") or secrets.token_hex(8)
    game = get_game(sid)
    output = game.look()
    actions = game.available_actions()
    return jsonify({
        "output": output,
        "actions": actions,
        "sid": sid,
        "state": game.state,
        "player": game.player.to_dict(),
        "enemy": game.enemy.to_dict() if game.enemy else None,
        "tile": game.current_tile().to_dict() if game.current_tile() else None
    })


@app.route("/api/game_state")
def api_game_state():
    sid = request.args.get("sid")
    if not sid:
        return jsonify({"error": "Missing session ID"}), 400
    game = get_game(sid)
    return jsonify(game.to_dict())


@app.route("/api/load", methods=["POST"])
def api_load():
    data = request.get_json()
    sid = data.get("sid") or secrets.token_hex(8)
    # Recreate game from saved state (assumes Game.from_json exists)
    loaded = Game.from_dict(data)
    game = create_game()
    game.ascii_tiles = False
    game.copy_from(loaded)
    SESSIONS[sid] = game
    output = game.look()
    actions = game.available_actions()
    # Add any extra fields you need (player, enemy, tile, etc.)
    resp = {"output": output, "actions": actions, "sid": sid}
    # Optionally add player/enemy/tile info if your API supports it
    if hasattr(game, "player"):
        resp["player"] = game.player.to_dict()
    if hasattr(game, "enemy") and game.enemy:
        resp["enemy"] = game.enemy.to_dict()
    if hasattr(game, "tile"):
        resp["tile"] = game.tile.to_dict()
    return jsonify(resp)


@app.route("/api/play")
def api_play():
    sid = request.args.get("sid")
    cmd = request.args.get("cmd", "")
    if not sid:
        return jsonify({"error": "Missing session ID"}), 400
    game = get_game(sid)
    output = game.execute_action(cmd) or "Unknown action."
    actions = game.available_actions()
    return jsonify({
        "output": output,
        "actions": actions,
        "sid": sid,
        "state": game.state,
        "player": game.player.to_dict(),
        "enemy": game.enemy.to_dict() if game.enemy else None,
        "tile": game.current_tile().to_dict() if game.current_tile() else None,
        "ended": game.ended
    })


@app.route("/api/new_game", methods=["POST"])
def api_new_game():
    sid = request.args.get("sid") or secrets.token_hex(8)
    size = int(request.args.get("size", 8))
    game = create_game()
    game.ascii_tiles = False
    SESSIONS[sid] = game
    output = game.look()
    actions = game.available_actions()
    return jsonify({
        "output": output,
        "actions": actions,
        "sid": sid,
        "state": game.state,
        "player": game.player.to_dict(),
        "enemy": game.enemy.to_dict() if game.enemy else None,
        "tile": game.current_tile().to_dict() if game.current_tile() else None
    })


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# SSE endpoint for real-time events
@app.route("/api/events")
def sse_events():
    sid = request.args.get("sid")

    def event_stream():
        if not sid or sid not in SESSIONS:
            yield "event: error\ndata: {\"error\": \"Missing or invalid session ID\"}\n\n"
            return
        game = SESSIONS[sid]
        q = []

        def handle_event(event):
            data = {"type": event.event_type, "payload": event.payload}
            q.append(f"data: {json.dumps(data)}\n\n")

        # Subscribe to game events
        game.event_manager.subscribe(handle_event)

        # Heartbeat every 10 seconds
        heartbeat_interval = 10
        last_heartbeat = time.time()

        while True:
            # Send queued events
            while q:
                yield q.pop(0)
            # Send heartbeat to keep connection alive
            if time.time() - last_heartbeat > heartbeat_interval:
                yield ": heartbeat\n\n"
                last_heartbeat = time.time()
            time.sleep(1)

    return app.response_class(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)
