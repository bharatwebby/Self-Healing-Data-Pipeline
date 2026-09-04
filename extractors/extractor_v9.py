def extract(raw):
    results = []
    items = raw.get('payload', {}).get('items', [])
    for item in items:
        external_id = int(item['id'])
        display_name = str(item['name'])
        amount_cents = int(round(item['amount'] * 100))
        results.append({
            'external_id': external_id,
            'display_name': display_name,
            'amount_cents': amount_cents
        })
    return results