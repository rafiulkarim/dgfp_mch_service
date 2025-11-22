from bs4 import BeautifulSoup
import requests
import csv
import json

url = "https://mis.dgfp.gov.bd/ss/mch_rep39/mch3_facility9.php"

div_code = ["01", "02"]

# Create a list to store all location objects
location_data = []

# Define division names (you might need to fetch these dynamically)
division_names = {
    "01": "Rajshahi",
    "02": "Khulna", 
    "03": "Barisal",
    "04": "Dhaka",
    "05": "Chattagram", 
    "06": "Sylhet",
    "07": "Rangpur",
    "08": "Mymensingh"
}

district_code = ['0111', '0112', '0113', '0114', "0202", "0203", "0207", "0210"]

all_thanas = []
for div in div_code:
    print(f"\nFetching districts for Division Code: {div}")
    print("=" * 50)
    
    payload = {
        "div_Code": div,
    }

    response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the district select element
    select = soup.find('select', {'name': 'dist_code'})

    # Extract all district options
    districts = []
    if select:
        for option in select.find_all('option'):
            value = option.get('value')
            text = option.get_text(strip=True)
            if value:  # Skip the first option which has no value
                districts.append({'value': value, 'text': text})
    else:
        print("District select element not found")
        continue

    # Process each district
    for district in districts:
        # Only process districts that are in our target list
        if district['value'] in district_code:
            print(f"\nDistrict: {district['text']} (Code: {district['value']})")
            print("-" * 40)
            
            # Payload for thana data
            dis_payload = {
                "div_Code": div,
                "dist_code": district['value'],
            }
            
            try:
                dis_response = requests.post(url, data=dis_payload)
                dis_soup = BeautifulSoup(dis_response.content, 'html.parser')

                # Find the thana select element
                dis_select = dis_soup.find('select', {'name': 'thana_code'})

                # Extract all thana options
                thanas = []
                if dis_select:
                    for dis_option in dis_select.find_all('option'):
                        dis_value = dis_option.get('value')
                        dis_text = dis_option.get_text(strip=True)
                        if dis_value:  # Skip the first option which has no value
                            thanas.append({'value': dis_value, 'text': dis_text})
                            
                            # Create location object
                            location_details_obj = {
                                # 'division_code': div,
                                # 'division_name': division_names.get(div, f"Division_{div}"),
                                # 'district_code': district['value'],
                                # 'district_name': district['text'],
                                # 'upazila_code': dis_value,
                                # 'upazila_name': dis_text
                                'div_Code': div,
                                'division_name': division_names.get(div, f"Division_{div}"),
                                'dist_code': district['value'],
                                'dist_name': district['text'],
                                'thana_code': dis_value,
                                'thana_name': dis_text
                            }
                            
                            location_code_obj = {
                                'div_Code': div,
                                # 'division_name': division_names.get(div, f"Division_{div}"),
                                'dist_code': district['value'],
                                # 'district_name': district['text'],
                                'thana_code': dis_value,
                                # 'upazila_name': dis_text
                            }
                            
                            location_data.append(location_details_obj)
                            all_thanas.append(location_details_obj)
                            print(f"  Upazila: {dis_text} (Code: {dis_value})")
                else:
                    print("  No upazila select element found")
                    
                print(f"  Total upazilas found: {len(thanas)}")
                
            except Exception as e:
                print(f"  Error fetching upazilas: {e}")
        else:
            # Skip districts not in our target list
            continue

    print(f"\nTotal districts found in division {div}: {len(districts)}")

# Print summary
print(f"\n{'='*60}")
print(f"TOTAL LOCATIONS COLLECTED: {len(location_data)}")
print(f"{'='*60}")

print(json.dumps(all_thanas, indent=4))

# print("\nFiltered Location Data (only target districts):")
# for thana in all_thanas:
#     print(thana)