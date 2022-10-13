import sys
sys.path.append('../')
from indexer.core import *

import threading
import queue

running = True

def worker_thread(id, queue):
    global running
    print(f"Worker [{id}] started")

    while running:
        try:
            page = queue.get()
            print(f"[{id}] Requesting url: {page.url}")
            request_page(page)
        except Exception as e:
            log_exception(e)
        finally:
            queue.task_done()

def main():
    global running
    workers_count = 5

    # Load domain
    if len(sys.argv) != 2:
        print("Not enough arguments! Using BBC Good Food by default!")
        domain = "https://www.bbcgoodfood.com/"
    else:
        domain = get_domain(sys.argv[1])

    # Load website
    if domain is None:
        print("Couldnt recognise the domain!")
        exit()
    else:
        website = load_or_create_website(domain)

    # Create workers
    worker_queue = queue.Queue(maxsize=workers_count)
    workers = []
    for id in range(workers_count):
        worker = threading.Thread(target=worker_thread, args=[id, worker_queue])
        worker.start()
        workers.append(worker)

    # Iterate through all new links
    while Page.objects(tags='new', domain=website).count() != 0:
        for page in Page.objects(tags='new', domain=website):
            worker_queue.put(page)

    # Wait for all to finish
    running = False
    for worker in workers:
        worker.join()
    print(f"Finished crawling for {website.domain}")

if __name__ == "__main__":
    db_connect()
    main()
