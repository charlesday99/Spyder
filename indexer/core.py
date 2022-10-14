from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from mongoengine import *
import traceback
import requests
import re

blocked_files = "^.*\.(jpg|jpeg|gif|pdf|png|m3u8|usdz|mp4|mp3|mov|zip|dmg|gz|xml|whl|xz|exe|tgz|msi|pkg|deb|chm|tar|rst|txt|json|yaml|toml|py|cfg|md|doc|docx|git|svg|egg|xlsx|xls|rss|gif|atom)$"
double_domains = ['.co.uk','.uk.com','org.uk','ac.uk','com.au','europa.eu','co.jp','com.br','edu.au','gov.au','com.tr','co.nz','co.za','com.cn','org.au']


def db_connect():
    with open('/etc/mongod.cred') as f:
        credentials = f.readlines()[0].strip()
        connect(host="mongodb://{}@78.110.170.126:27017/data".format(credentials))
        print('Connected to MongoDB!')


def is_file(url):
    if len(re.findall(blocked_files, url)) != 0:
        return True
    else:
        return False


def log_exception(e):
    with open("/tmp/exceptions.log","a+") as f:
        f.write(traceback.format_exc())
        f.write("At:\n")
        f.write(str(datetime.now()))
        f.write("---\n")


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
            if parsed.netloc[-6:] in double_domains:
                url = parsed.netloc.split('.')[-3:]
                return f"{parsed.scheme}://{url[0]}.{url[1]}.{url[2]}/"
            else:
                url = parsed.netloc.split('.')[-2:]
                return f"{parsed.scheme}://{url[0]}.{url[1]}/"


def load_or_create_website(domain, linked_from=None):
    websites = Website.objects(domain=domain)

    # Check if website exists
    if len(websites) == 0:
        try:
            website = Website(domain=domain).save()

            if linked_from is not None:
                Page(url=domain, domain=website, tags=["new"], linked_from=[linked_from]).save()
            else:
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

    # Save title
    if soup.title is not None:
        page.title = soup.title.get_text()
        page.save()

    # Find and save description
    description = None
    for tag in soup.find_all("meta"):
        if 'name' in tag.attrs and 'description' in tag.attrs['name']:
            if 'content' in tag.attrs:
                description = tag.attrs['content']
    
    if description is not None:
        page.description = description[0:300].strip()
        page.save()

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

        # Skip http links
        if href[0:5] == 'http:':
            continue
        
        if verbose:
            print(f"        Processing: {href}")

        # Check for relative url
        if href[0:5] == 'https':

            if get_domain(href) == None:
                continue

            # Check if link is an external domain
            if get_domain(href) != website.domain:
                external_website = load_or_create_website(get_domain(href), linked_from=website)
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

        if resp.status_code == 200 and 'Content-Type' in resp.headers:
            
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


class Website(Document):
    domain = StringField(required=True, unique=True)
    ranking = IntField()
    last_ranked = DateTimeField(
        default=datetime.utcfromtimestamp(0)
    )
    tags = ListField(StringField())
    meta = {'indexes': [{
        'fields': ['$domain'],
        'default_language': 'english',
    }]}


class Page(Document):
    title = StringField()
    description = StringField(max_length=300)
    url = StringField(required=True, unique=True)

    domain = ReferenceField(Website, reverse_delete_rule=CASCADE, required=True)
    linked_from = ListField(ReferenceField(Website))
    tags = ListField(StringField())

    meta = {'indexes': [
        {'fields': ['$title', "$description"],
         'default_language': 'english',
         'weights': {'title': 10, 'content': 5}
        }
    ]}
    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.save()
