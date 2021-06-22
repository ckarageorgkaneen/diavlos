#!/usr/bin/env python3
from diavlos.src.site import Site
import json
import requests

site = Site()
site.login(auto=True)


def _fetch_english_title(greek):
    url = "https://reg-diavlos.gov.gr/fields/organisations.php?org=" + greek

    x = requests.get(url)

    json_data = json.loads(x.text)
    if json_data:
        english_name = json_data['title_en']
        return english_name
    else:
        return None


for page in site._client.allpages(namespace='9004'):
    page_title = page.page_title
    page_text = page.text()

    row = "|registry_org_main="
    rowLen = len(row)
    new_line = "\n"

    index = page_text.find(row)
    if index != -1:
        new_lineIndex = page_text.find(new_line, index)
        rowToChange = page_text[index:new_lineIndex]
        greek_registry_org_main = page_text[index + rowLen:new_lineIndex]

        english_registry_org_main = _fetch_english_title(greek_registry_org_main)
        if english_registry_org_main is not None:
            newRow = rowToChange.replace(greek_registry_org_main, english_registry_org_main)

            if page_text.find(rowToChange) != -1:
                page.edit(page_text.replace(
                    rowToChange, newRow
                ))
                print(f'Changed {page_title}', flush=True)
            else:
                print(f'Not Changed {page_title}', flush=True)
        else:
            print(f'Cannot find {page_title}', flush=True)
