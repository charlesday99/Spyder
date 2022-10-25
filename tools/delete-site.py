import sys
sys.path.append('../')
from indexer.core import *

import threading
import queue

def main():

    # Load domain
    if len(sys.argv) != 2:
        print("Not enough arguments!")
        exit(1)
    else:
        domain = get_domain(sys.argv[1])

    # Load website
    if domain is None:
        print("Couldnt recognise the domain!")
        exit(1)
    else:
        website = load_or_create_website(domain)
    page_count = Page.objects(domain=website).count()

    print(f"Website {domain} has {page_count} page(s)")
    if "y" not in input("Are you sure it should be deleted? "):
        exit()

    print(f"Deleting domain: {domain}")
    website.delete()

if __name__ == "__main__":
    db_connect()
    main()
