#!/usr/bin/env python3
import mwclient
site = mwclient.Site('diadikasies.dev.grnet.gr', scheme='http', path='/')
site.login('Master','4BQpC2625FBD')
with open('orgs.txt', 'r') as f:
    orgs = [org.strip('\n') for org in f.readlines()]
print(orgs)
for page_title in orgs:
    new_title = f'Φορέας:{page_title}'
    page = site.pages[page_title]
    new_page = site.pages[new_title]
    try:
        if not new_page.exists:
            page.move(new_title)
            print(new_title)
    except Exception as e:
        print(e)

