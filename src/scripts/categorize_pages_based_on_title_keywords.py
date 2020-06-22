#!/usr/bin/env python3
import mwclient
import unicodedata
en_to_gr_char_table = str.maketrans('ahkzxbnmetyio','αηκζχβνμετυιο')
KEYWORD_CATEGORIES = {
    'αιτησ': 'Αιτήσεις',
    'βεβαιωσ': 'Βεβαιώσεις',
    'καταγγελ': 'Καταγγελίες',
    'μητρω': 'Μητρώα',
    'συνταξ': 'Συντάξεις'
}
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
site = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
site.login('Master','4BQpC2625FBD')
for page in site.categories['Διαδικασίες']:
    plain_title = strip_accents(page.page_title).lower().translate(en_to_gr_char_table)
    for keyword, category in KEYWORD_CATEGORIES.items():
        category_link = '[[Category:{}]]'.format(category)
        page_text = page.text()
        if keyword in plain_title and category_link not in page_text:
            if not site.categories[category].exists:
                mwclient.page.Page(site, 'Category:' + category).edit('')
            page.edit(page_text + '\n' + category_link)
