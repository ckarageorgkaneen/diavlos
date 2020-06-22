#!/usr/bin/env python3
import mwclient
import unicodedata
CATMORE_TEMPLATE = '{{cat more}}'
site = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
site.login('Master','4BQpC2625FBD')
for cat in site.allcategories():
    cat_page_text = cat.text()
    if CATMORE_TEMPLATE not in cat_page_text:
        cat.edit(cat_page_text + '\n{}'.format(CATMORE_TEMPLATE))
