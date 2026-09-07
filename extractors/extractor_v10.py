def extract(raw):
    result = []
    for item in raw:
        result.append({
            'external_id': int(item['id']),
            'display_name': str(item['name']),
            'amount_cents': int(item['amount'] * 100)
        })
    return result