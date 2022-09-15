import sys

from core import *


def main():
    # Load url
    if len(sys.argv) != 2:
        print("Not enough arguments!")
        exit()
    else:
        url = sys.argv[1]

    # Check url
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:

        # Process page
        website = load_or_create_website(get_domain(url))
        save_or_create_page(url, website)
        page = Page.objects(url=url)[0]

        print(f"Requesting url: {url}")
        request_page(page, verbose=True)

        print(f"Finished crawling for {url}!")
    else:
        print(f"Failed to load {url}!")


if __name__ == "__main__":
    main()
