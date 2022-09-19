from core import *

def main():
    for website in Website.objects():
        print(f"Calculating rank for: {website.domain}")
        linked_from_domains = set()

        for page in Page.objects(domain=website):
            for linked_domain in page.linked_from:
                linked_from_domains.add(linked_domain)

        rank = len(linked_from_domains)
        print(f"Setting rank as: {rank}")
        website.ranking = rank
        website.save()


if __name__ == "__main__":
    main()
