import sys
sys.path.append('../')
from indexer.core import *

from datetime import datetime, timedelta
import time

def main():
    while True:
        try:
            threshold = datetime.now() - timedelta(days=10)
            raw_query = {'last_ranked': {'$lt': threshold }}

            count = Website.objects(__raw__=raw_query).count()
            print(f"Calculating rank for {count} websites:")

            for website in Website.objects(__raw__=raw_query):
                linked_from_domains = set()

                for page in Page.objects(domain=website).only('linked_from').no_dereference():
                    for linked_domain in page.linked_from:
                        linked_from_domains.add(linked_domain.id)

                rank = len(linked_from_domains)
                print(f"Setting rank for {website.domain} as: {rank}")
                website.ranking = rank
                website.last_ranked = datetime.now()

                website.save()
        except Exception as e:
            log_exception(e)
        finally:
            print('\nSleeping for 30 minutes...\n')
            time.sleep(1800)

if __name__ == "__main__":
    db_connect()
    main()
