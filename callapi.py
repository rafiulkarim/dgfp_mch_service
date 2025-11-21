import requests

url = "https://mis.dgfp.gov.bd/ss/mch_rep39/mch3_facility9.php"

# Your form data as a dictionary
# payload = {
#     "div_Code": "01",
#     "dist_code": "0112",
#     "thana_code": "011201",
#     "H_Mon": "10",
#     "H_Year": "2024",
#     "H_Mon1": "10",
#     "H_Year1": "2025"
# }

payload = {
    "div_Code": "01",
    "dist_code": "District",
    "thana_code": "Upazila",
    "H_Mon": "Month",
    "H_Year": "Year",
    "H_Mon1": "Select Month",
    "H_Year1": "Select Year"
}

# Send the POST request with form data
response = requests.post(url, data=payload)

# Check if the request was successful
# print(f"Status Code: {response.status_code}")

# Print the response text from the server
print(response.text)