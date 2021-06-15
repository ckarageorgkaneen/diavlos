#!/usr/bin/env python3

from diavlos.src.site import Site
from diavlos.src.service import Service

site = Site()
site.login(auto=True)


query = "[[Category:Κατάλογος Διαδικασιών]][[Process total duration steps digital min::1]]"
for answer in site._client.ask(query):
    page_name = answer['fulltext']
    page = site.pages(page_name)
    service = Service().fetch_by_name(page_name)

    text = page.text()

    process_total_duration_steps_digital_minROW = "|process_total_duration_steps_digital_min=1\n"

    process_evidence_step_digital_total_numberROW = "|process_evidence_step_digital_total_number=0\n"
    process_steps_digitalROW = "{{process steps digital\n"

    exists = False

    if text.find(process_evidence_step_digital_total_numberROW) != - \
            1 or text.find(process_steps_digitalROW) != -1:

        page.edit(page.text().replace(
            process_total_duration_steps_digital_minROW, ""
        ))
        print(f'{page_name} changed', flush=True)

print(f'Done', flush=True)
