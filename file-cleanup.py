from core import *

def main():
    print("Searching new links:")
    for page in Page.objects(tags='new'):
        if is_file(page.url):
            page.remove_tag('new')
            page.add_tag('disabled_file')
            print(f"[new] Disabled file: {page.url}")

    print("Searching disabled links:")
    for page in Page.objects(tags='disabled'):
        if is_file(page.url):
            page.remove_tag('disabled')
            page.add_tag('disabled_file')
            print(f"[disabled] Disabled file: {page.url}")

    print("Searching files links:")
    for page in Page.objects(tags='file'):
        if is_file(page.url):
            page.remove_tag('file')
            page.add_tag('disabled_file')
            print(f"[file] Disabled file: {page.url}")
        else:
            print(f"Uncaught file: {page.url}")


if __name__ == "__main__":
    main()
