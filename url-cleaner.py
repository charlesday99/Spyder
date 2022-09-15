import sys

from core import *

blocked_files = [
    '.pdf',
    '.jpg',
    '.jpeg',
    '.m3u8',
    '.usdz'
]


def main():
    for page in Page.objects(tags='new'):

        for blocked_file in blocked_files:
            if blocked_file in page.url:
                changed = False

                if 'new' in page.tags:
                    page.tags.remove('new')
                    changed = True

                if 'disabled' not in page.tags:
                    page.tags.append('disabled')
                    changed = True

                if changed:
                    page.save()
                    print(f"Disabled {page.url}")

                continue


if __name__ == "__main__":
    main()
