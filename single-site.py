import threading
import queue
import sys

from core import *


def main():
    # Load domain
    if len(sys.argv) != 2:
        print("Not enough arguments!")
        exit()
    else:
        domain = get_domain(sys.argv[1])

    # Load website
    if domain is None:
        print("Couldnt recognise the domain!")
        exit()
    else:
        website = load_or_create_website(domain)

    # Iterate through all new links
    while Page.objects(tags='new', domain=website).count() != 0:
        for page in Page.objects(tags='new', domain=website):
            print(f"Requesting url: {page.url}")
            request_page(page, verbose=True)

    print(f"Finished crawling for {website.domain}!")


if __name__ == "__main__":
    main()
