import sys
sys.path.append('../')
from indexer.core import *

import time

def main():
    while True:
        for website in Website.objects():
            linked_from_domains = set()

            for page in Page.objects(domain=website):
                for linked_domain in page.linked_from:
                    linked_from_domains.add(linked_domain)

            rank = len(linked_from_domains)
            print(f"Setting rank for {website.domain} as: {rank}")
            website.ranking = rank

            website.save()
            time.sleep(10)

if __name__ == "__main__":
    db_connect()
    main()
