import os, threading, time, logging
from flask import Flask, jsonify

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.get("/")
def root():
    return jsonify(ok=True, timestamp=time.time())

def keep_alive():
    def run():
        port = int(os.environ.get("PORT", 3000))
        app.run(host="0.0.0.0", port=port, use_reloader=False)
    t = threading.Thread(target=run, daemon=True)
    t.start()
