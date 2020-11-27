#!/usr/bin/env python3
from services.src.site import Site

for page in Site().categories['Κατάλογος Φορέων']:
    page_title = page.page_title
    if 'Φορέας:' not in page_title:
        print(page_title)
