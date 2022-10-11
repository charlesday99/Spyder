import sys
sys.path.append('../')
from indexer.core import *

from flask import Flask, render_template, request, abort, send_from_directory
from datetime import datetime, timedelta
from threading import Thread
import time
import os

app = Flask(__name__,static_url_path='')
db_connect()

page_count = 0
ranked_count = 0


@app.route("/")
def search():
    date = datetime.now().strftime('%A %d %B').replace(' 0', ' ')
    return render_template('search.html', date=date)


@app.route("/search")
def results():
    global page_count
    query = request.args.get('q')
    page = request.args.get('page') or 0

    if query is not None:
        page_start = int(page)*10
        page_end = int(page)*10+10

        results = Page.objects.search_text(query).order_by('$text_score')[page_start:page_end]

        return render_template(
            'results.html',
            query=query,
            results=results,
            pages_count="{:,}".format(page_count),
        )
    else:
        abort(400)


@app.route("/rankings")
def rankings():
    global ranked_count
    page = request.args.get('page') or 0
    page_start = int(page)*20
    page_end = int(page)*20+20

    results = Website.objects.order_by('-ranking')[page_start:page_end]

    return render_template(
        'rankings.html',
        results=results,
        ranked_count="{:,}".format(ranked_count),
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')


def updatePageCount():
    global page_count
    global ranked_count
    while True:
        page_count = Page.objects(tags='processed').count()

        threshold = datetime.now() - timedelta(days=10)
        raw_query = {'last_ranked': {'$gt': threshold }}
        ranked_count = Website.objects(__raw__=raw_query).count()

        time.sleep(600)


if __name__ == "__main__":
    Thread(target=updatePageCount).start()
    app.run(host='0.0.0.0')
