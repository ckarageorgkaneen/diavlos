#!/usr/bin/env python3
import re
import mwclient
FIELD_NAME = 'Provision Means'
site = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
site.login('Master','4BQpC2625FBD')
for page in site.categories['Διαδικασίες']: 
    new_text = page.text()
    if FIELD_NAME not in new_text:
        idx = new_text.index('}}')
        page.edit(new_text[:idx] + '|{}=Ψηφιακά\n'.format(FIELD_NAME) + new_text[idx:])

