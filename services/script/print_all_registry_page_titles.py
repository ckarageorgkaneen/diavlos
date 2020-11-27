#!/usr/bin/env python3
from services.src.site import Site

for page in Site().categories['Κατάλογος Μητρώων']:
    page_title = page.page_title
    if 'Μητρώο:' not in page_title:
        print(page_title)
