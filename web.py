#!/usr/bin/env python3
"""
Simple web interface for Oakheart Tales (text MUD).

Run: python3 web.py
Then open http://127.0.0.1:8000/ in your browser.

No external dependencies; uses Python's built-in wsgi server.
"""

from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import secrets
import html
from typing import Dict, Tuple, Callable, Optional

from game import Game
from persistence import save_game, load_game, SAVE_FILE


# Very small in-memory session store. Not for production use.
SESSIONS: Dict[str, Game] = {}


def get_or_create_sid(environ) -> str:
    # Try cookie first
    cookies = environ.get("HTTP_COOKIE", "")
    sid = None
    for part in cookies.split(";"):
        if part.strip().startswith("sid="):
            sid = part.strip()[4:]
            break
    if not sid:
        sid = secrets.token_urlsafe(16)
    return sid


def response(status: str, body: str, headers: Optional[list] = None):
    hdrs = [("Content-Type", "text/html; charset=utf-8")]
    if headers:
        hdrs.extend(headers)
    return status, hdrs, body.encode("utf-8")


def layout(title: str, content: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background: #0b0e14; color: #e6e1cf; margin: 0; }}
    header {{ background: #11151c; padding: 12px 16px; border-bottom: 1px solid #2a2f3a; }}
    main {{ padding: 16px; display: grid; gap: 16px; grid-template-columns: 1fr; }}
    .panel {{ background: #11151c; border: 1px solid #2a2f3a; border-radius: 8px; padding: 12px; }}
    .output pre {{ white-space: pre-wrap; word-wrap: break-word; margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .actions form {{ display: inline-block; margin: 4px 6px 0 0; }}
    button {{ background: #2a2f3a; color: #e6e1cf; border: 1px solid #3a3f4a; border-radius: 6px; padding: 8px 12px; cursor: pointer; }}
    button:hover {{ background: #343a46; }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .hint {{ color: #a6accd; font-size: 0.9em; }}
  </style>
  <link rel=\"icon\" href=\"data:,\" />
  <meta name=\"color-scheme\" content=\"dark light\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <script>window.addEventListener('keydown', e => {{
    const map = {{
      'ArrowUp': 'n', 'w':'w', 'ArrowLeft':'w', 'a':'w', 'ArrowDown':'s', 's':'s', 'ArrowRight':'e', 'd':'e'
    }};
    const cmd = map[e.key];
    if (cmd) {{ e.preventDefault(); const f=document.getElementById('cmdform'); f.cmd.value=cmd; f.submit(); }}
  }});</script>
  <meta name=\"robots\" content=\"noindex,nofollow\" />
  <meta name=\"referrer\" content=\"no-referrer\" />
  <meta name=\"cross-origin-opener-policy\" content=\"same-origin\" />
  <meta name=\"cross-origin-embedder-policy\" content=\"require-corp\" />
  <meta http-equiv=\"Permissions-Policy\" content=\"interest-cohort=()\" />
  <meta http-equiv=\"X-Content-Type-Options\" content=\"nosniff\" />
</head>
<body>
  <header><strong>Oakheart Tales</strong> — Web</header>
  <main>{content}</main>
</body>
</html>
"""


def start_page() -> str:
    return layout(
        "Oakheart Tales — Start",
        """
        <div class=\"grid\">
          <div class=\"panel\">
            <h3>Start</h3>
            <form method=\"GET\" action=\"/new\">
              <label>Map size:
                <select name=\"size\">
                  <option>5</option>
                  <option>3</option>
                  <option>7</option>
                </select>
              </label>
              <button type=\"submit\">New Game</button>
            </form>
            <form method=\"GET\" action=\"/load\" style=\"margin-top:8px\">
              <button type=\"submit\">Load Saved Game</button>
            </form>
            <p class=\"hint\">Tip: Use arrow keys or WASD to move once in game.</p>
          </div>
        </div>
        """,
    )


def game_view(sid: str, game: Game, last_output: str) -> str:
    escaped = html.escape(last_output)
    stats = game.stats()
    stats_esc = html.escape(stats)
    return layout(
        "Oakheart Tales — Play",
        f"""
        <div class=\"grid\">
          <div class=\"panel output\">
            <pre>{escaped}</pre>
          </div>
          <div class=\"panel\">
            <h3>Actions</h3>
            <form id=\"cmdform\" method=\"GET\" action=\"/play\">
              <input type=\"hidden\" name=\"sid\" value=\"{sid}\" />
              <input type=\"hidden\" name=\"cmd\" value=\"look\" />
              <div>
                <button onclick=\"this.form.cmd.value='n'\" type=\"submit\">North ↑</button>
                <button onclick=\"this.form.cmd.value='s'\" type=\"submit\">South ↓</button>
                <button onclick=\"this.form.cmd.value='w'\" type=\"submit\">West ←</button>
                <button onclick=\"this.form.cmd.value='e'\" type=\"submit\">East →</button>
              </div>
              <div style=\"margin-top:8px\">
                <button onclick=\"this.form.cmd.value='look'\" type=\"submit\">Look</button>
                <button onclick=\"this.form.cmd.value='map'\" type=\"submit\">Map</button>
                <button onclick=\"this.form.cmd.value='stats'\" type=\"submit\">Stats</button>
                <button onclick=\"this.form.cmd.value='rest'\" type=\"submit\">Rest</button>
                <button onclick=\"this.form.cmd.value='shop'\" type=\"submit\">Shop</button>
                <button onclick=\"this.form.cmd.value='inv'\" type=\"submit\">Inventory</button>
                <button onclick=\"this.form.cmd.value='save'\" type=\"submit\">Save</button>
                <button onclick=\"this.form.cmd.value='load'\" type=\"submit\">Load</button>
              </div>
            </form>
          </div>
          <div class=\"panel\">
            <h3>Character</h3>
            <pre>{stats_esc}</pre>
          </div>
        </div>
        """,
    )


def handle_play(game: Game, cmd: str) -> str:
    cmd = (cmd or "").strip().lower()
    if cmd in ("n", "north"):
        return game.move(0, -1)
    if cmd in ("s", "south"):
        return game.move(0, 1)
    if cmd in ("e", "east"):
        return game.move(1, 0)
    if cmd in ("w", "west"):
        return game.move(-1, 0)
    if cmd in ("look", "l"):
        return game.look()
    if cmd in ("map", "m"):
        return game.map()
    if cmd in ("stats", "character", "c"):
        return game.stats()
    if cmd in ("rest", "r"):
        return game.rest()
    if cmd in ("inv", "inventory", "i"):
        p = game.player
        return f"Inventory: Potions x{p.potions}; Gold {p.gold}"
    if cmd in ("shop",):
        return game.shop()
    if cmd in ("save",):
        save_game(game, SAVE_FILE)
        return f"Game saved to {SAVE_FILE}."
    if cmd in ("load",):
        loaded = load_game(SAVE_FILE)
        if loaded:
            game.copy_from(loaded)
            return "Game loaded.\n\n" + game.look()
        return "No save found or save file invalid."
    # default
    return "Unknown command."


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    qs = parse_qs(environ.get("QUERY_STRING", ""))

    sid = get_or_create_sid(environ)
    set_cookie_header = ("Set-Cookie", f"sid={sid}; Path=/; HttpOnly; SameSite=Lax")

    def finish(resp):
        status, hdrs, body = resp
        # ensure cookie is always set
        hdrs.append(set_cookie_header)
        start_response(status, hdrs)
        return [body]

    if path == "/":
        return finish(response("200 OK", start_page()))

    if path == "/new":
        size = 5
        try:
            size_str = qs.get("size", ["5"])[0]
            size = int(size_str)
            if size not in (3, 5, 7):
                size = 5
        except Exception:
            size = 5
        # Non-interactive game for web: auto-resolve prompts and combat
        web_input = (lambda prompt="": "a")
        web_print = (lambda *args, **kwargs: None)
        game = Game.new_random(size=size, input_fn=web_input, print_fn=web_print, interactive=False)
        SESSIONS[sid] = game
        body = game_view(sid, game, game.look())
        return finish(response("200 OK", body))

    if path == "/load":
        loaded = load_game(SAVE_FILE)
        if not loaded:
            return finish(response("200 OK", layout("Load", "<div class=panel><p>No save found or save file invalid.</p><p><a href='/'>Back</a></p></div>")))
        # Configure loaded game for web
        loaded.input_fn = (lambda prompt="": "a")
        loaded.print_fn = (lambda *args, **kwargs: None)
        loaded.interactive = False
        SESSIONS[sid] = loaded
        body = game_view(sid, loaded, loaded.look())
        return finish(response("200 OK", body))

    if path == "/play":
        game = SESSIONS.get(sid)
        if not game:
            # redirect to start
            return finish(response("302 Found", "", headers=[("Location", "/")]))
        # Ensure non-interactive configuration (in case of stale session)
        if getattr(game, "interactive", True):
            game.input_fn = (lambda prompt="": "a")
            game.print_fn = (lambda *args, **kwargs: None)
            game.interactive = False
        cmd = qs.get("cmd", ["look"])[0]
        out = handle_play(game, cmd)
        body = game_view(sid, game, out)
        return finish(response("200 OK", body))

    return finish(response("404 Not Found", layout("Not found", "<div class=panel><p>Not found</p><p><a href='/'>&larr; Home</a></p></div>")))


def main(host: str = "127.0.0.1", port: int = 8000):
    httpd = make_server(host, port, app)
    print(f"Serving on http://{host}:{port} … Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
