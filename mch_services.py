from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://mis.dgfp.gov.bd/ss/mch_rep39/mch3_facility9.php"

# Define headers for Table 5 with additional location columns
TABLE_5_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "SI", "Facility",
    "1st Dose", "2nd Dose", "3rd Dose", "4th Dose", "5th Dose",
    "1st Visit", "2nd Visit", "3rd Visit", "4th Visit",
    "Counseling on Post partum FP method",
    "No. of mother Suffering from APH",
    "Inj.antenatal costeroides in(24-34 weeks)",
    "No.of Pregnant mother Receive Misoprostol",
    "Normal", "C-Section",
    "Others (Forcep/Vacuum/Breech)",
    "No. of delivery followed (AMTSL)",
    "No. of mother uses Partograph",
    "No. of mother Suffering from IPH",
    "No. of services post abortion care",
    "No. of pre-eclampsia patient",
    "1st Visit (PNC)", "2nd Visit (PNC)", "3rd Visit (PNC)", "4th Visit (PNC)",
    "No. of mother counseled on FP method after Postpartum",
    "No. of mother suffering from PPH after Delivery"
]

# Define headers for Table 7 with additional location columns
TABLE_7_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "SI", "Facility",
    "Wrapping after Birth within 1 minute",
    "No. of uses 7.1% chlorhexidine digluconate for umbilical cord care",
    "No. of newborn touch skin-care after Gluconate umbilical cord care",
    "No. of newborn breastfeeding (First 24 hours)",
    "No. of newborn resitated with bag-mask",
    "1st Visit", "2nd Visit", "3rd Visit", "4th Visit",
    "No. of Reffered Complicated Pregnant Mother in antenatal period",
    "No. of Reffered Complicated Pregnant Mother in Delivery period",
    "No. of Reffered Complicated Pregnant Mother in postnatal period",
    "No. of Reffered patient to Newborn taken by MgSO4",
    "No. of Reffered complication acceptors",
    "No. of ECP Referred",
    "Treatment/Advised", "Reffered",
    "Counseling on Adolescence change",
    "Counseling on marriage and adolescent girl received pregnancy",
    "Child No. of adolescent received IFA",
    "Treatment on RTI/STD",
    "Counseling on RTI/STD",
    "Counseling on diversified food",
    "Counseling on prevention of adolescent and violence",
    "Counseling on prevention and cure for mental problems and drug addiction",
    "No. of adolescent girl counseled on Sanitary Pad",
    "Reffered (Adolescent)",
    "No. of Treatment on RTI/STI infection",
    "No. of MR(MVA) services",
    "No. of MR Service By Medicine",
    "Total VIA Positive",
    "Total VIA Negative",
    "Total CBE Positive",
    "Total Negative"
]

# Define headers for Table 9 with additional location columns
TABLE_9_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "SI", "Facility",
    "No. of neonatal start KMC",
    "No. of neonatal start KMC hospital delivery",
    "No. of child discharge",
    "No. of child discharge on request",
    "No. of child discontinue KMC services",
    "No. of child reffered for complication",
    "No. of death received KMC services",
    "No. of neonatal KMC followup",
    "BCG (after birth)",
    "1/Child age 6 weeks",
    "2/Child age 10 weeks",
    "3/Child age 14 weeks",
    "1/Child age 6 weeks (PCV)",
    "2/Child age 10 weeks (PCV)",
    "3/Child age 14 weeks (PCV)",
    "1/Child age 6 weeks (BOPV)",
    "2/Child age 10 weeks (BOPV)",
    "3/Child age 14 weeks (BOPV)",
    "1/Child age 6 weeks (IPV)",
    "2/Child age 14 weeks (IPV)",
    "1/Child age 9 months",
    "2/Child age 15 months",
    "Live Birth",
    "Low birth weight Newborn (weight <2500gm)",
    "Low birth weight Newborn (weight <2000gm)",
    "Low birth weight Newborn (Before 37 weeks)",
    "Fresh",
    "Macerated",
    "Total still birth",
    "Neo-Death Maternal",
    "Maternal Death",
    "Male",
    "Female",
    "Child Male (0-1)year",
    "Child Female (0-5)year",
    "Others",
    "Total",
    "Female (Outdoor)",
    "Child (0-1) year",
    "Child (0-5) year",
    "Total (Outdoor)",
    "No. of Facility Health Education",
    "No. of School Health Education by SACMO"
]

# Table configuration
TABLE_CONFIG = {
    5: {"headers": TABLE_5_HEADERS, "index": 4},
    7: {"headers": TABLE_7_HEADERS, "index": 6},
    9: {"headers": TABLE_9_HEADERS, "index": 8}
}

# Facility keywords
facility_keywords = [
    'atpara', 'baniajan', 'duaz', 'loneshwar', 
    'sarmusia', 'sunai', 'sukhari', 'teligati',
    'mch', 'uh&fwc', 'dispensary', 'clinic', 'unit'
]

# Division mapping
DIVISION_MAP = {
    "01": "Rajshahi",
    "02": "Khulna", 
    "03": "Barisal",
    "04": "Dhaka",
    "05": "Chattagram", 
    "06": "Sylhet",
    "07": "Rangpur",
    "08": "Mymensingh"
}

def extract_data_rows(table, facility_keywords):
    """Extract data rows from table and remove last row if it's a total row"""
    rows = table.find_all('tr')
    data_rows = []
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_data = []
        
        for cell in cells:
            text = ' '.join(cell.get_text(strip=True).split())
            colspan = int(cell.get('colspan', 1))
            row_data.extend([text] * colspan)
        
        if row_data and len(row_data) > 2:
            first_cell = row_data[0].lower() if row_data[0] else ""
            second_cell = row_data[1].lower() if len(row_data) > 1 and row_data[1] else ""
            
            is_data_row = (
                first_cell.isdigit() or
                'total' in first_cell or
                'upazila' in first_cell or
                any(kw in first_cell or kw in second_cell for kw in facility_keywords)
            )
            
            if is_data_row:
                data_rows.append(row_data)
    
    # Remove the last row if it's a total row
    if data_rows and 'total' in data_rows[-1][0].lower():
        data_rows = data_rows[:-1]
        print(f"  Removed total row from table")
    
    return data_rows

def get_all_thana_codes():
    """Get all thana codes from all divisions and districts"""
    # div_codes = ["01", "02"]
    div_codes = ["01", "02", "03", "04", "05", "06", "07", "08"]
    all_thana_codes = []
    
    for div in div_codes:
        print(f"\nFetching districts for Division Code: {div}")
        print("=" * 50)
        
        payload = {"div_Code": div}
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
                if value:
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
                if dis_select:
                    for dis_option in dis_select.find_all('option'):
                        dis_value = dis_option.get('value')
                        dis_text = dis_option.get_text(strip=True)
                        if dis_value:
                            thana_info = {
                                'div_code': div,
                                'div_name': DIVISION_MAP.get(div, f"Division_{div}"),
                                'district_code': district['value'],
                                'district_name': district['text'],
                                'thana_code': dis_value,
                                'thana_name': dis_text
                            }
                            all_thana_codes.append(thana_info)
                            print(f"  Thana Value: {dis_value}, Thana: {dis_text}")
                else:
                    print("  No thana select element found")
                    
                print(f"  Total thanas found: {len([t for t in all_thana_codes if t['district_code'] == district['value']])}")
                
            except Exception as e:
                print(f"  Error fetching thanas: {e}")

        print(f"\nTotal districts found in division {div}: {len(districts)}")
    
    return all_thana_codes

def scrape_data_for_thana_codes(thana_codes, output_dir="scraped_tables"):
    """Scrape data for given thana codes"""
    os.makedirs(output_dir, exist_ok=True)

    # Initialize CSV files with headers
    for table_num, config in TABLE_CONFIG.items():
        filename = f"{output_dir}/table_{table_num}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(config["headers"])
        print(f"📄 Created: {filename} with {len(config['headers'])} columns")

    # Loop through all thana codes
    for i, thana_info in enumerate(thana_codes, 1):
        thana_code = thana_info['thana_code']
        
        payload = {
            "div_Code": thana_info['div_code'],
            "dist_code": thana_info['district_code'],
            "thana_code": thana_code,
            "H_Mon": "10",
            "H_Year": "2024",
            "H_Mon1": "10",
            "H_Year1": "2025"
        }
        
        print(f"\n{'='*60}")
        print(f"🔄 Fetching data for Thana: {thana_info['thana_name']} (Code: {thana_code})")
        print(f"   District: {thana_info['district_name']}, Division: {thana_info['div_name']}")
        print(f"{'='*60}")
        
        response = requests.post(url, data=payload)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        
        print(f"Status Code: {response.status_code}")
        print(f"Total tables found: {len(tables)}")
        
        # Process each target table
        for table_num, config in TABLE_CONFIG.items():
            table_index = config["index"]
            headers = config["headers"]
            filename = f"{output_dir}/table_{table_num}.csv"
            
            if table_index < len(tables):
                table = tables[table_index]
                data_rows = extract_data_rows(table, facility_keywords)
                
                # Append data to CSV
                with open(filename, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    for row_data in data_rows:
                        # Add location information as first columns
                        row_with_location = [
                            thana_info['div_code'],        # Division_Code
                            thana_info['div_name'],        # Division_Name
                            thana_info['district_code'],   # District_Code
                            thana_info['district_name'],   # District_Name
                            thana_info['thana_code'],      # Thana_Code
                            thana_info['thana_name'],      # Thana_Name
                        ] + row_data
                        
                        # Pad if needed
                        while len(row_with_location) < len(headers):
                            row_with_location.append('')
                        # Trim if too long
                        row_with_location = row_with_location[:len(headers)]
                        
                        writer.writerow(row_with_location)
                
                print(f"  ✅ Table {table_num}: Added {len(data_rows)} rows")
            else:
                print(f"  ⚠️ Table {table_num}: Not available")

    print(f"\n{'='*60}")
    print(f"✅ All data from {len(thana_codes)} thanas saved to '{output_dir}' folder!")
    print(f"   - table_5.csv (Woman Received TT, ANC, Delivery, PNC)")
    print(f"   - table_7.csv (PNC Neo-natal, Reffered, Adolescent, Screening)")
    print(f"   - table_9.csv (KMC, Child Services, Indoor, Still Birth)")
    print(f"{'='*60}")

def main():
    """Main function to run the complete scraping process"""
    print("🚀 Starting Bangladesh Health Data Scraper")
    print("=" * 60)
    
    # Option 1: Get all thana codes automatically
    print("\n1. 🔍 Discovering all thana codes...")
    all_thana_codes = get_all_thana_codes()
    
    print(f"\n🎯 Total thanas discovered: {len(all_thana_codes)}")
    
    # Option 2: Use specific thana codes (for testing)
    # specific_thana_codes = [
    #     {
    #         'div_code': '01', 
    #         'div_name': 'Chattagram',
    #         'district_code': '0112', 
    #         'district_name': 'Test District',
    #         'thana_code': '011201', 
    #         'thana_name': 'Test Thana'
    #     }
    # ]
    
    # Scrape data for all discovered thana codes
    print("\n2. 📊 Starting data scraping for all thanas...")
    scrape_data_for_thana_codes(all_thana_codes)
    
    print("\n✅ Scraping completed successfully!")

if __name__ == "__main__":
    main()