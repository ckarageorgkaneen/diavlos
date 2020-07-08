#!/usr/bin/env python3
import mwclient
import pandas
import requests
import pickle
OLDSITEURL = 'el.diadikasies.gr'
DOCUMENTSCOLKW = 'Απαραίτητα Δικαιολογητικά'
oldsite = mwclient.Site(OLDSITEURL, path='/')
newsite = mwclient.Site('snf-13326.ok-kno.grnetcloud.net', scheme='http', path='/dev/')
newsite.login('Master','4BQpC2625FBD')
documents = set()
for page in oldsite.allpages():
    print(page.page_title)
    response = requests.get('https://{}/{}'.format(OLDSITEURL, page.page_title.replace(' ', '_')))
    try:
        tables = pandas.read_html(response.content, encoding='utf-8', header=0)
    except ValueError:
    # No tables found
        continue
    documents_table = None
    for table in tables:
        if DOCUMENTSCOLKW in table:
            documents_table = table
    if documents_table is None:
        continue
    for doc in documents_table[DOCUMENTSCOLKW]:
        doc_str = str(doc)
        if doc_str != 'nan':
            documents.add(doc_str)
# print(documents)
with open('dikaiologhtika.pickle', 'wb') as handle:
    pickle.dump(documents, handle, protocol=pickle.HIGHEST_PROTOCOL)

