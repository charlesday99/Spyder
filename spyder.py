import threading
import queue

from core import *


def worker(id, queue):
    print(f"Worker [{id}] started")

    while True:
        page = queue.get()

        print(f"[{id}] Requesting url: {page.url}")
        request_page(page)

        queue.task_done()


def main():
    workers_count = 10

    # Create default website
    load_or_create_website(get_domain("https://python.org/"))

    # Create workers
    worker_queue = queue.Queue(maxsize=workers_count)
    for id in range(workers_count):
        threading.Thread(target=worker, args=[id, worker_queue]).start()

    # Iterate through all new pages
    while Page.objects(tags='new').count() != 0:

        for page in Page.objects(tags='new'):
            worker_queue.put(page)


if __name__ == "__main__":
    main()
