#!/usr/bin/env python3
import mwclient
site = mwclient.Site('diadikasies.dev.grnet.gr', scheme='http', path='/')
site.login('Master','4BQpC2625FBD')
orgs = []

def foreis(title):
    if title in orgs:
        return
    category = iter(site.categories[title])
    try:
        first_page = next(category)
    except StopIteration:
        return
    orgs.append(title)
    print(title)
    for page in category:
        foreis(page.page_title)
foreis('Φορείς')
