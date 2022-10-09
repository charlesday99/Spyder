import sys
sys.path.append('../')
from indexer.core import *

from flask import Flask, render_template, request, abort, send_from_directory
from datetime import datetime
import os

app = Flask(__name__,static_url_path='')
db_connect()

@app.route("/")
def search():
    date = datetime.now().strftime('%A %d %B').replace(' 0', ' ')
    return render_template('search.html', date=date)

@app.route("/search")
def results():
    query = request.args.get('q')
    page = request.args.get('page') or 0

    if query is not None:
        page_start = int(page)*10
        page_end = int(page)*10+10
        results = Page.objects.search_text(query).order_by('$text_score')[page_start:page_end]
        return render_template(
            'results.html',
            query=query,
            results=results
        )
    else:
        abort(400)

@app.route("/rankings")
def rankings():
    return render_template('rankings.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
