def extract(raw):
    items = raw['payload']['items']
    result = []
    for item in items:
        result.append({
            'external_id': item['id'],
            'display_name': item['name'],
            'amount_cents': round(item['amount'] * 100)
        })
    return result