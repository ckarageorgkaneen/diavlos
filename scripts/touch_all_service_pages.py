#!/usr/bin/env python3
from diavlos.src.site import Site
site = Site()
site.login(auto=True)
process_namespaces = [
    '9002',  # ΔΔ
    '9006',  # ΥΕ
    '9008',  # ΠΕ
    '9010',  # ΠΔ
]
for ns in process_namespaces:
    for page in site._client.allpages(namespace=ns):
        page.touch()
        print(f'{page.page_title} touched.')
