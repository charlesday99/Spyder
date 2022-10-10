import sys
sys.path.append('../')
from indexer.core import *

import threading
import queue

def worker(id, queue):
    print(f"Worker [{id}] started")

    while True:
        try:
            website = queue.get()
            linked_from_domains = set()

            for page in Page.objects(domain=website):
                for linked_domain in page.linked_from:
                    linked_from_domains.add(linked_domain)

            rank = len(linked_from_domains)
            print(f"[{id}] Setting rank for {website.domain} as: {rank}")
            website.ranking = rank
            website.save()

        except Exception as e:
            log_exception(e)
        finally:
            queue.task_done()

def main():
    workers_count = 5

    worker_queue = queue.Queue(maxsize=workers_count)
    for id in range(workers_count):
        threading.Thread(target=worker, args=[id, worker_queue]).start()

    for website in Website.objects():
        worker_queue.put(website)

    print("\nFinished!\n")


if __name__ == "__main__":
    db_connect()
    main()
