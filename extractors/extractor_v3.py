def extract(raw):
    result = []
    items = raw['payload']['items']
    for item in items:
        result.append({
            'external_id': item['id'],
            'display_name': item['name'],
            'amount_cents': round(item['amount'] * 100)
        })
    return result