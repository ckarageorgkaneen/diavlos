#!/usr/bin/env python3
from diavlos.src.site import Site
site = Site()
site.auto_login()
process_namespaces = [
    '9000',  # Φορέας
    '9002',  # ΔΔ
    '9004',  # Μητρώο
    '9006',  # ΥΕ
    '9008',  # ΠΕ
    '9010',  # ΠΔ
    '9012',  # Ιδιωτικός Φορέας
]
for ns in process_namespaces:
    for page in site._client.allpages(namespace=ns):
        page.touch()
        print(f'{page.page_title} touched.')
