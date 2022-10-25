import sys
sys.path.append('../')
from indexer.core import *

from flask import Flask, render_template, request, abort, send_from_directory, redirect
from datetime import datetime, timedelta
from threading import Thread
import time
import os

app = Flask(__name__,static_url_path='')
db_connect()

page_count = 0
ranked_count = 0

ranks_page_size = 20
search_page_size = 10


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
        search_query = SearchQuery(text=query, time=datetime.now()).save()

        page_start = int(page)*search_page_size
        page_end = int(page)*search_page_size+search_page_size

        results_count = Page.objects.search_text(query).order_by('$text_score').count()
        results = Page.objects.search_text(query).order_by('$text_score')[page_start:page_end]

        page_numbers = min(int(results_count/search_page_size) + 1, 10)
        return render_template(
            'results.html',
            query=query,
            results=results,
            search_id=search_query.id,
            pages_count="{:,}".format(page_count),
            results_count="{:,}".format(results_count),
            page_numbers=page_numbers,
            current_page_number=page,
        )
    else:
        abort(400)


@app.route("/rankings")
def rankings():
    global ranked_count
    page = request.args.get('page') or 0
    page_start = int(page)*ranks_page_size
    page_end = int(page)*ranks_page_size+ranks_page_size

    results = Website.objects.order_by('-ranking')[page_start:page_end]

    return render_template(
        'rankings.html',
        results=results,
        ranked_count="{:,}".format(ranked_count),
        page_numbers=10,
        current_page_number=page,
    )


@app.route("/redirect/<page_id>")
def redirect_page(page_id):
    search = SearchQuery.objects(id=request.args.get('search', ''))
    page = Page.objects(id=page_id)

    if len(page) == 1:
        page = page[0]
        if len(search) == 1:
            SearchRedirect(
                query=search[0],
                page=page,
                time=datetime.now()
            ).save()
        return redirect(page.url)
    else:
        abort(404)


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
