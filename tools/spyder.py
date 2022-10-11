import sys
sys.path.append('../')
from indexer.core import *

import threading
import queue

def worker(id, queue):
    print(f"Worker [{id}] started")

    while True:
        try:
            page = queue.get()

            print(f"[{id}] Requesting url: {page.url}")
            request_page(page)

        except Exception as e:
            log_exception(e)
        finally:
            queue.task_done()


def main():
    workers_count = 5

    # Create default website
    load_or_create_website(get_domain("https://bbc.co.uk/"))

    # Create workers
    worker_queue = queue.Queue(maxsize=workers_count)
    for id in range(workers_count):
        threading.Thread(target=worker, args=[id, worker_queue]).start()

    while True:
        for page in Page.objects(tags='new'):
            worker_queue.put(page)


if __name__ == "__main__":
    db_connect()
    main()
