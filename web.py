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
from typing import Dict, Tuple, Callable, Optional, List

from engine.game import Game

from json_loader import JsonLoader
from text_loader import TextLoader
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
  <script>
  function saveGame() {{
     fetch('/save_state?sid=' + encodeURIComponent(document.querySelector('[name="sid"]').value))
        .then(r => r.text())
        .then(txt => {{
            localStorage.setItem('oakheart_save', txt);
            alert('Game saved to browser storage.');
        }});
  }}
  function loadGame(sid) {{
    const data = localStorage.getItem('oakheart_save');
    if (!data) {{
        alert('No saved game in browser storage.');
        return;
    }}
    if (!sid) {{
        sid = encodeURIComponent(document.querySelector('[name="sid"]').value);
    }}
    fetch('/load_state?sid=' + sid, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: data
    }})
    .then(r => r.text())
    .then(txt => {{
        alert('Game loaded from browser storage. Reloading page.');
        window.location.href = '/play?sid=' + sid;
    }});
  }}
  </script>
</head>
<body>
  <header><strong>Oakheart Tales</strong> — Web</header>
  <main>{content}</main>
</body>
</html>
"""


def start_page(sid) -> str:
    return layout(
        "Oakheart Tales — Start",
        f"""
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
            <button type="button" onclick="loadGame('{sid}')">Load Game</button>
            <p class=\"hint\">Tip: Use arrow keys or WASD to move once in game.</p>
          </div>
        </div>
        """,
    )


def game_view(sid: str, game: Game, last_output: str) -> str:
    escaped = html.escape(last_output)
    stats = game.stats()
    stats_esc = html.escape(stats)
    actions: List[dict] = game.available_actions()

    # Group actions by category for a tidy layout
    grouped: Dict[str, List[dict]] = {}
    for a in actions:
        grouped.setdefault(a.get("category", "general"), []).append(a)

    # Render action buttons dynamically. Disabled actions are shown but disabled with title.
    group_html_parts: List[str] = []
    for cat, lst in grouped.items():
        btns = []
        for a in lst:
            aid = a["id"]
            if aid == "save":
                continue  # skip redundant save action
            label = html.escape(a["label"])  # safe
            enabled = bool(a.get("enabled", True))
            reason = html.escape(a.get("reason")) if a.get("reason") else ""
            attr = "" if enabled else " disabled title=\"" + reason + "\""
            btns.append(f"<button onclick=\"this.form.cmd.value='{aid}'\" type=\"submit\"{attr}>{label}</button>")
        group_html_parts.append(
            f"<div style=\"margin-top:8px\"><div class=\"hint\">{html.escape(cat.capitalize())}</div>" + "\n".join(
                btns) + "</div>"
        )

    actions_html = "\n".join(group_html_parts)

    # Add Save/Load controls which are interface-level actions
    sys_controls = (
        "<div style=\"margin-top:8px\">"
        "<div class=\"hint\">System</div>"
        "<button type=\"button\" onclick=\"saveGame()\">Save</button>"
        "<button type=\"button\" onclick=\"loadGame()\">Load</button>"
        "</div>"
    )

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
              {actions_html}
              {sys_controls}
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
    # Interface-level commands
    if cmd in ("__save", "save"):
        save_game(game.to_dict(), game.save_file)
        return f"Game saved to {game.save_file}."
    if cmd in ("__load", "load"):
        loaded = load_game(game.save_file)
        if loaded:
            game.copy_from(Game.from_dict(loaded))
            return "Game loaded.\n\n" + game.look()
        return "No save found or save file invalid."

    # Delegate to game actions API
    out = game.execute_action(cmd)
    if out is not None:
        return out
    return f"Unknown command: {cmd}"


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
        return finish(response("200 OK", start_page(sid)))

    if path == "/new":
        size = 5
        try:
            size_str = qs.get("size", ["5"])[0]
            size = int(size_str)
            if size not in (3, 5, 7):
                size = 5
        except Exception:
            size = 5
        data_loader = JsonLoader()
        tiles = data_loader.load("data/tileset.json")
        game = Game.new_random(size=size, tiles=tiles)
        game.save_fn = save_game
        game.load_fn = load_game
        game.data_loader = data_loader
        game.ascii_loader = TextLoader("data/rooms")
        game.load_configurations("data/enemies.json")
        game.save_file = f"{sid}_{environ.get('REMOTE_ADDR', 'unknown')}.sav"
        SESSIONS[sid] = game
        body = game_view(sid, game, game.look())
        return finish(response("200 OK", body))

    if path == "/save_state":
        game = SESSIONS.get(sid)
        if not game:
            return finish(response("200 OK", ""))
        from json import dumps
        return finish(response("200 OK", dumps(game.to_dict())))

    if path == "/load_state":
        try:
            from json import loads
            length = int(environ.get("CONTENT_LENGTH", "0"))
            raw_body = environ["wsgi.input"].read(length)
            data = loads(raw_body)
            game = Game.from_dict(data)
            SESSIONS[sid] = game
            body = game_view(sid, game, "Loaded game!\n" + game.look())
            return finish(response("200 OK", body))
        except Exception:
            return finish(response("400 Bad Request", "Invalid save data."))

    if path == "/load":
        loaded = load_game(SAVE_FILE)
        if not loaded:
            return finish(response("200 OK", layout("Load",
                                                    "<div class=panel><p>No save found or save file invalid.</p><p><a href='/'>Back</a></p></div>")))
        game = Game.from_dict(loaded)
        game.save_fn = save_game
        game.load_fn = load_game
        game.data_loader = JsonLoader()
        game.ascii_loader = TextLoader("data/rooms")
        game.load_configurations("data/enemies.json")
        game.save_file = f"{sid}_{environ.get('REMOTE_ADDR', 'unknown')}.sav"
        SESSIONS[sid] = Game.from_dict(loaded)
        body = game_view(sid, game, game.look())
        return finish(response("200 OK", body))

    if path == "/play":
        game = SESSIONS.get(sid)
        game.save_file = f"{sid}_{environ.get('REMOTE_ADDR', 'unknown')}.sav"
        if not game:
            # redirect to start
            return finish(response("302 Found", "", headers=[("Location", "/")]))
        cmd = qs.get("cmd", ["look"])[0]
        out = handle_play(game, cmd)
        body = game_view(sid, game, out)
        if game.ended:
            SESSIONS.pop(sid, None)
            body = "Game ended. <script>window.location.href='/'</script>"
        return finish(response("200 OK", body))

    return finish(response("404 Not Found", layout("Not found",
                                                   "<div class=panel><p>Not found</p><p><a href='/'>&larr; Home</a></p></div>")))


def main(host: str = "127.0.0.1", port: int = 8000):
    httpd = make_server(host, port, app)
    print(f"Serving on http://{host}:{port} … Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
