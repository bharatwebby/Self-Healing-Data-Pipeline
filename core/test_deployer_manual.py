from core.deployer import deploy
from core.monitor import run_once

WORKING_V2_CODE = '''
def extract(raw):
    items = raw['payload']['items']
    result = []
    for item in items:
        result.append({
            'external_id': item['id'],
            'display_name': item['name'],
            'amount_cents': round(item['amount'] * 100),
        })
    return result
'''

print("=== BEFORE DEPLOY (should FAIL, still on v1 which only handles flat) ===")
run_once()

version = deploy(WORKING_V2_CODE)
print(f"\n=== DEPLOYED as v{version} ===")

print("\n=== AFTER DEPLOY (should now SUCCEED automatically) ===")
run_once()