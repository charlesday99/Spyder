from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import re

from models import *

blocked_files = "^.*\.(jpg|jpeg|gif|pdf|png|m3u8|usdz|mp4|mp3|mov|zip|dmg|gz|xml|whl|xz|exe|tgz|msi|pkg|deb|chm|tar|rst|txt|json|yaml|toml|py|cfg|md|doc|docx|git|svg|egg)$"

# Load credentials & connect to MongoDB
with open('/etc/mongod.cred') as f:
    credentials = f.readlines()[0].strip()

connect(host="mongodb://{}@iterator.me:27017/data".format(credentials))
print("Connected to MongoDB...")


def is_file(url):
    if len(re.findall(blocked_files, url)) != 0:
        return True
    else:
        return False


def alert(text, border):
    print(f"    {border}")
    print(f"    {border} {str(text)}")
    print(f"    {border}")


def get_domain(url):
    parsed = urlparse(url)
    if parsed.netloc == '':
        return None
    else:
        if parsed.netloc.count('.') == 0:
            alert(f"Bad domain: {url}", '!')
            return None
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

    # Check if website exists
    if len(websites) == 0:
        print("Trying to create website")
        try:
            website = Website(domain=domain).save()
            Page(url=domain, domain=website, tags=["new"]).save()

            alert(f"Created website: {website.domain}", '|')
            return website
        except:
            return Website.objects(domain=domain)[0]
    else:
        return websites[0]


def save_or_create_page(link, domain, linked_from=None):
    pages = Page.objects(url=link)

    # Check if page exists
    if len(pages) == 0:
        try:
            page = Page(url=link, domain=domain, tags=["new"]).save()
            print(f"    Saved: {link}")
        except:
            print(f"    NotUniqueError: {link}")
            return
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

        # Validate href
        if href is None:
            continue
        if href == '/':
            continue
        if '#' in href:
            continue
        if 'mailto:' in href:
            continue
        if is_file(href):
            continue

        # Remove parameters
        if '?' in href:
            href = href.split('?')[0]
        if len(href) == 0:
            continue

        # Upgrade to https
        if href[0:5] == 'http:':
            href = 'https:' + href[5:]
        
        if verbose:
            print(f"        Processing: {href}")

        # Check for relative url
        if href[0:5] == 'https':

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
            
            if 'text/html' in resp.headers['Content-Type']:
                process_page(page, resp.text, verbose=verbose)
                page.tags.append('processed')
            else:
                alert(f"File found: {resp.headers['Content-Type']}", '!')
                page.tags.append('file')
        else:
            print(f"    !!! Request failed with code {resp.status_code} !!!")
            page.tags.append('failed')

    except requests.exceptions.RequestException as e:
        print(f"    !!! RequestException raised !!!")
        page.tags.append('failed')

    if 'new' in page.tags:
        page.tags.remove('new')
    page.save()
