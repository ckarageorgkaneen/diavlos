#!/usr/bin/env python3
import re
import mwclient
site = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
site.login('Master','4BQpC2625FBD')
# page = site.pages['Άδεια φύτευσης οινοποιήσιμων ποικιλιών αμπέλου']
# new_text = re.sub(r"<br \/>([^\*]+:\s*https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*))", r'*\1', page.text())
for page in site.categories['Διαδικασίες']:
    page.edit(page.text().replace('<br />', '\n*'))
# page.edit(new_text)
