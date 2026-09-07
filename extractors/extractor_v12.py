import xml.etree.ElementTree as ET

def extract(raw):
    root = ET.fromstring(raw)
    results = []
    
    for record in root.findall('.//record'):
        id_elem = record.find('id')
        name_elem = record.find('name')
        amount_elem = record.find('amount')
        
        external_id = int(id_elem.text) if id_elem is not None and id_elem.text else 0
        display_name = str(name_elem.text) if name_elem is not None and name_elem.text else ''
        amount_cents = int(float(amount_elem.text) * 100) if amount_elem is not None and amount_elem.text else 0
        
        results.append({
            'external_id': external_id,
            'display_name': display_name,
            'amount_cents': amount_cents
        })
    
    return results