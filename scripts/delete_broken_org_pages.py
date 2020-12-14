#!/usr/bin/env python3
from diavlos.src.site import Site

site = Site()
site.auto_login()

for page in site.categories['Κατάλογος Φορέων']:
    page_title = page.page_title
    if page_title.startswith('Broken/'):
        page.delete()
        print(f'{page_title} deleted.')
