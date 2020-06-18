#! /usr/bin/env python3
import urllib.request
import json
url = 'https://hr.apografi.gov.gr/api/public/organizations'
urlobj = urllib.request.urlopen(url)
orgs = json.loads(urlobj.read().decode('utf-8'))
print(*['"{}"'.format(orgdict['preferredLabel'].replace('"', '""')) for orgdict in orgs['data']], sep='\n')
