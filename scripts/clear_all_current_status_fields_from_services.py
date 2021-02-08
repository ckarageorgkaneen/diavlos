#!/usr/bin/env python3
from diavlos.src.site import Site
from diavlos.src.service import Service

CURRENT_STATUS_FIELD = 'process_current_status='
FILLED_CURRENT_STATUS_FIELD = f'{CURRENT_STATUS_FIELD}Υπό επεξεργασία'

site = Site()
site.auto_login()

for page in site.categories[Service.CATEGORY_NAME]:
    page.edit(page.text().replace(
        FILLED_CURRENT_STATUS_FIELD, CURRENT_STATUS_FIELD))
    print(f'Cleared current status field from {page.page_title}')
