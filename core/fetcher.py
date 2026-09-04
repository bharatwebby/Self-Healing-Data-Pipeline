import requests
import xml.etree.ElementTree as ET

SOURCE_URL = "http://127.0.0.1:9000/data"

def fetch_raw():
    """Fetches ONE complete dataset, following pagination internally if the
    source is paginated. Generated extractor code always receives a single,
    already-complete blob — it never needs network access of its own."""
    response = requests.get(SOURCE_URL)
    content_type = response.headers.get("content-type", "")

    if "xml" in content_type:
        return _fetch_all_xml_pages(response.text)

    try:
        return response.json()
    except ValueError:
        return response.text

def _fetch_all_xml_pages(first_page_xml: str) -> str:
    all_records_xml = []
    page_xml = first_page_xml

    while True:
        root = ET.fromstring(page_xml)
        records_el = root.find("records")
        if records_el is not None:
            for record in records_el:
                all_records_xml.append(ET.tostring(record, encoding="unicode"))

        next_page_el = root.find("next_page")
        next_page_text = next_page_el.text if next_page_el is not None else None
        if not next_page_text or next_page_text == "null":
            break

        response = requests.get(SOURCE_URL, params={"page": next_page_text})
        page_xml = response.text

    return f"<response><records>{''.join(all_records_xml)}</records></response>"