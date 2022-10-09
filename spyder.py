import threading
import queue

from core import *


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

    # Iterate through all new pages
    while Page.objects(tags='new').count() != 0:

        for website in Website.objects():
            print(f"\nScanning website: {website.domain}")
            page_count = workers_count * 2

            for page in Page.objects(tags='new', domain=website):
                if page_count != 0:
                    worker_queue.put(page)
                    page_count -= 1
                else:
                    break


if __name__ == "__main__":
    main()
