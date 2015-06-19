from flask import Flask
from flask import render_template
from performance import get_dashboard_stats
app = Flask(__name__)

@app.route("/")
def stats():
  return render_template('index.html', stats=get_dashboard_stats())
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)