from core.fetcher import fetch_raw

raw = fetch_raw()
print("TYPE:", type(raw))
print("-----RAW OUTPUT-----")
print(raw)
print("--------------------")
if isinstance(raw, str):
    print("Number of <record> tags found:", raw.count("<record>"))