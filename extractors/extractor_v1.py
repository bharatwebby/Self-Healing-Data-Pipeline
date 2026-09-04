"""
Extractor v1 — only knows how to read the FLAT shape.
Contract every extractor must follow: extract(raw) -> list[dict]
matching TargetRecord's fields exactly.
"""

def extract(raw):
    records = []
    for item in raw:
        records.append({
            "external_id": item["id"],
            "display_name": item["name"],
            "amount_cents": round(item["amount"] * 100),  # dollars -> cents
        })
    return records