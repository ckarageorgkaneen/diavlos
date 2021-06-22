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


for page in site.categories['Κατάλογος Φορέων']:
    page_title = page.page_title
    page_text = page.text()

    row = "|gov_org_subOrganizationOf="
    rowLen = len(row)
    new_line = "\n"

    index = page_text.find(row)
    if index != -1:
        new_lineIndex = page_text.find(new_line, index)
        rowToChange = page_text[index:new_lineIndex]
        greek_gov_org_subOrganizationOf = page_text[index + rowLen:new_lineIndex]

        english_gov_org_subOrganizationOf = _fetch_english_title(greek_gov_org_subOrganizationOf)

        if english_gov_org_subOrganizationOf is not None:
            newRow = rowToChange.replace(greek_gov_org_subOrganizationOf, english_gov_org_subOrganizationOf)

            if page_text.find(rowToChange) != -1:
                page.edit(page_text.replace(
                    rowToChange, newRow
                ))
                print(f'Changed {page_title}', flush=True)
            else:
                print(f'Not Changed {page_title}', flush=True)
        else:
            print(f'Cannot find {page_title}', flush=True)