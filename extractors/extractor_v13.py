def extract(raw):
    results = []
    items = raw.get('payload', {}).get('items', [])
    for item in items:
        results.append({
            'external_id': int(item['id']),
            'display_name': str(item['name']),
            'amount_cents': int(item['amount'] * 100)
        })
    return results