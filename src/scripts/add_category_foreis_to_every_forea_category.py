#!/usr/bin/env python3
import mwclient
import unicodedata
FOREIS_CATEGORY = "[[Category:Φορείς]]"
site = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
site.login('Master','4BQpC2625FBD')
for i, page in enumerate(site.categories['Φορείς']):
    print(i)
    # if i < YOUR_NUM_OFFSET_HERE:
    #    continue
    category = site.categories[page.page_title]
    category_page_text = category.text()
    if FOREIS_CATEGORY not in category_page_text:
        category.edit('{}\n{}'.format(category_page_text, FOREIS_CATEGORY))

