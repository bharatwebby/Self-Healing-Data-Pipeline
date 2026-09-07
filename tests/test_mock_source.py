import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from mock_source.main import app

client = TestClient(app)


def test_flat_mode_returns_a_plain_top_level_list():
    client.post("/admin/mutate", params={"mode": "flat"})
    resp = client.get("/data")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 25
    assert {"id", "name", "amount"} <= body[0].keys()


def test_nested_mode_wraps_records_in_payload_items():
    client.post("/admin/mutate", params={"mode": "nested"})
    resp = client.get("/data")

    body = resp.json()
    assert "payload" in body
    assert "items" in body["payload"]
    assert len(body["payload"]["items"]) == 25


def test_xml_paginated_mode_returns_valid_xml_with_working_pagination():
    client.post("/admin/mutate", params={"mode": "xml_paginated"})

    page1 = client.get("/data", params={"page": 1})
    assert "xml" in page1.headers["content-type"]
    root1 = ET.fromstring(page1.text)
    assert len(root1.find("records")) == 10
    assert root1.find("next_page").text == "2"

    page3 = client.get("/data", params={"page": 3})
    root3 = ET.fromstring(page3.text)
    assert len(root3.find("records")) == 5  # 25 records, page size 10 -> last page has 5
    assert root3.find("next_page").text == "null"


def test_malicious_mode_embeds_the_injection_payload_as_plain_data():
    client.post("/admin/mutate", params={"mode": "malicious"})
    resp = client.get("/data")

    body = resp.json()
    poisoned_name = body["payload"]["items"][0]["name"]
    assert "IGNORE ALL PREVIOUS INSTRUCTIONS" in poisoned_name


def test_underlying_data_is_identical_across_modes_only_presentation_changes():
    """Mirrors the real-world scenario the assignment describes: the data
    itself doesn't change, only the shape it's delivered in."""
    client.post("/admin/mutate", params={"mode": "flat"})
    flat_first_id = client.get("/data").json()[0]["id"]

    client.post("/admin/mutate", params={"mode": "nested"})
    nested_first_id = client.get("/data").json()["payload"]["items"][0]["id"]

    assert flat_first_id == nested_first_id
