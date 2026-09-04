import xml.etree.ElementTree as ET

def extract(raw):
    root = ET.fromstring(raw)
    records = root.find('records')
    
    result = []
    for record in records.findall('record'):
        external_id = int(record.find('id').text)
        display_name = record.find('name').text
        amount = float(record.find('amount').text)
        amount_cents = round(amount * 100)
        
        result.append({
            'external_id': external_id,
            'display_name': display_name,
            'amount_cents': amount_cents
        })
    
    return result