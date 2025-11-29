# dev_server.py
from livereload import Server
import web

server = Server(web.app)
# Watch your project files for changes
server.watch('web.py')
server.watch('game/')
server.serve(port=8000, host='127.0.0.1', open_url_delay=1)