from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://mis.dgfp.gov.bd/ss/mch_rep39/mch3_facility9.php"

div_code = ["01", "02"] 

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
                        print(f"  Thana Value: {dis_value}, Thana: {dis_text}")
            else:
                print("  No thana select element found")
                
            print(f"  Total thanas found: {len(thanas)}")
            
        except Exception as e:
            print(f"  Error fetching thanas: {e}")

    print(f"\nTotal districts found in division {div}: {len(districts)}")