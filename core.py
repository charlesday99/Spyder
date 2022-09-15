from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

from models import *

# Load credentials & connect to MongoDB
with open('/etc/mongod.cred') as f:
    credentials = f.readlines()[0].strip()

connect(host="mongodb://{}@iterator.me:27017/data".format(credentials))
print("Connected to MongoDB...")


def get_domain(url):
    parsed = urlparse(url)
    if parsed.netloc == '':
        return None
    else:
        if parsed.netloc.count('.') == 1:
            return f"{parsed.scheme}://{parsed.netloc}/"
        else:
            # Strip subdomains
            if parsed.netloc[-6:] == ".co.uk":
                url = parsed.netloc.split('.')[-3:]
                return f"{parsed.scheme}://{url[0]}.{url[1]}.{url[2]}/"
            else:
                url = parsed.netloc.split('.')[-2:]
                return f"{parsed.scheme}://{url[0]}.{url[1]}/"


def load_or_create_website(domain):
    websites = Website.objects(domain=domain)

    if len(websites) == 0:
        website = Website(domain=domain).save()
        Page(url=domain, domain=website, tags=["new"]).save()

        print(f"    Created website: {website.domain}")
        return website
    else:
        return websites[0]


def save_or_create_page(link, domain, linked_from=None):
    pages = Page.objects(url=link)

    if len(pages) == 0:
        try:
            page = Page(url=link, domain=domain, tags=["new"]).save()
            print(f"    Saved: {link}")
        except mongoengine.errors.NotUniqueError:
            print(f"    NotUniqueError: {link}")
    else:
        page = pages[0]

    if linked_from != None:
        if linked_from not in page.linked_from:
            page.linked_from.append(linked_from)
            page.save()
            print(f"    Added link from {linked_from.domain} to {link}")


def process_page(page, html, verbose=False):
    soup = BeautifulSoup(html, 'html.parser')
    website = page.domain

    # Iterate though all links
    for a_tag in soup.findAll('a'):
        href = a_tag.get('href')

        # Check href is valid
        if href is None:
            continue
        if href == '/':
            continue
        if '#' in href:
            continue
        if 'mailto:' in href:
            continue
        if '?' in href:
            href = href.split('?')[0]
        if len(href) == 0:
            continue
        if href[-4:] == '.pdf':
            continue
        if href[-4:] == '.jpg':
            continue
        if href[0:5] == 'http:':
            continue

        if verbose:
            print(f"    Processing: {href}")

        # Check for relative url
        if 'https' == href[0:5]:

            if get_domain(href) == None:
                continue

            # Check if link is an external domain
            if get_domain(href) != website.domain:
                external_website = load_or_create_website(get_domain(href))
                save_or_create_page(href, external_website, linked_from=website)
            else:
                save_or_create_page(href, website)

        else:
            # Remove leading slash
            if href[0] == '/':
                href = href[1:]

            # Create full href & save
            save_or_create_page(website.domain + href, website)


def request_page(page, verbose=False):
    try:
        resp = requests.get(page.url, timeout=5)

        if resp.status_code == 200:
            process_page(page, resp.text, verbose=verbose)
            page.tags.append('processed')
        else:
            print(f"    !!! Request failed with code {resp.status_code} !!!")
            page.tags.append('failed')

    except requests.exceptions.RequestException as e:
        print(f"    !!! RequestException raised !!!")
        page.tags.append('failed')

    if 'new' in page.tags:
        page.tags.remove('new')
    page.save()
