from flask import Flask
from flask import render_template
from performance import get_dashboard_stats
from flask.ext.cache import Cache
app = Flask(__name__)

cache = Cache(app,config={'CACHE_TYPE': 'simple'})

@app.route("/")
@cache.cached(timeout=172800)
def stats():
  return render_template('index.html', stats=get_dashboard_stats())
 
@app.route("/clearcache")
def clear_cache():
  with app.app_context():
    cache.clear()
  return 'Cleared Cache'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)