from merged_data import get_data
import json

# data = get_data()

# print(data)

a = {
    "H_Mon": "09",
    "H_Year": "2025",
    "H_Mon1": "09",
    "H_Year1": "2025",
    "div_Code": "02",
    "div_name": "Khulna",
    "dist_code": "0210",
    "dist_name": "Khulna1",
    "thana_code": "021007",
    "thana_name": "Shatkhira"
}

# Remove multiple keys using a loop
keys_to_remove = ['div_name', 'dist_name', 'thana_name']
for key in keys_to_remove:
    a.pop(key, None)

# Display as formatted JSON
print(json.dumps(a, indent=4))