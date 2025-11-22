from bs4 import BeautifulSoup
import requests
import csv
import os
from merged_data import get_data

url = "https://mis.dgfp.gov.bd/ss/mch_rep39/mch3_facility9.php"

# Define headers for Table 5 with month/year columns
TABLE_5_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "Month_Code", "Month_Name", "Year",
    "SI", "Facility",
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

# Define headers for Table 7 with month/year columns
TABLE_7_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "Month_Code", "Month_Name", "Year",
    "SI", "Facility",
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

# Define headers for Table 9 with month/year columns
TABLE_9_HEADERS = [
    "Division_Code", "Division_Name", "District_Code", "District_Name", 
    "Thana_Code", "Thana_Name", "Month_Code", "Month_Name", "Year",
    "SI", "Facility",
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

TABLE_CONFIG = {
    5: {"headers": TABLE_5_HEADERS, "index": 4},
    7: {"headers": TABLE_7_HEADERS, "index": 6},
    9: {"headers": TABLE_9_HEADERS, "index": 8}
}

DIVISION_MAP = {
    "01": "Rajshahi", "02": "Khulna", "03": "Barisal", "04": "Dhaka",
    "05": "Chattagram", "06": "Sylhet", "07": "Rangpur", "08": "Mymensingh"
}

MONTH_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}

facility_keywords = [
    'atpara', 'baniajan', 'duaz', 'loneshwar', 'sarmusia', 'sunai', 
    'sukhari', 'teligati', 'mch', 'uh&fwc', 'dispensary', 'clinic', 'unit'
]

def extract_data_rows(table, facility_keywords):
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
                first_cell.isdigit() or 'total' in first_cell or 'upazila' in first_cell or
                any(kw in first_cell or kw in second_cell for kw in facility_keywords)
            )
            if is_data_row:
                data_rows.append(row_data)
    if data_rows and 'total' in data_rows[-1][0].lower():
        data_rows = data_rows[:-1]
    return data_rows

def scrape_data(output_dir="scraped_tables"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all payload data
    all_payloads = get_data()
    print(f"📊 Total payloads to process: {len(all_payloads)}")
    
    # Initialize CSV files
    for table_num, config in TABLE_CONFIG.items():
        filename = f"{output_dir}/table_{table_num}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(config["headers"])
        print(f"📄 Created: {filename}")

    # Loop through all payloads
    for i, payload in enumerate(all_payloads, 1):
        div_code = payload.get('div_Code', '')
        dist_code = payload.get('dist_code', '')
        thana_code = payload.get('thana_code', '')
        month_code = payload.get('H_Mon', '')
        year = payload.get('H_Year', '')
        
        # Get names from maps or payload
        div_name = DIVISION_MAP.get(div_code, payload.get('div_name', ''))
        dist_name = payload.get('dist_name', '')
        thana_name = payload.get('thana_name', '')
        month_name = MONTH_MAP.get(month_code, '')
        
        print(f"\n[{i}/{len(all_payloads)}] 🔄 Processing: {thana_name} | {month_name} {year}")
        
        try:
            
            
            response = requests.post(url, data=payload, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')
            
            for table_num, config in TABLE_CONFIG.items():
                table_index = config["index"]
                headers = config["headers"]
                filename = f"{output_dir}/table_{table_num}.csv"
                
                if table_index < len(tables):
                    table = tables[table_index]
                    data_rows = extract_data_rows(table, facility_keywords)
                    
                    with open(filename, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        for row_data in data_rows:
                            row_with_info = [
                                div_code, div_name, dist_code, dist_name,
                                thana_code, thana_name, month_code, month_name, year
                            ] + row_data
                            
                            while len(row_with_info) < len(headers):
                                row_with_info.append('')
                            row_with_info = row_with_info[:len(headers)]
                            writer.writerow(row_with_info)
                    
                    print(f"  ✅ Table {table_num}: {len(data_rows)} rows")
                else:
                    print(f"  ⚠️ Table {table_num}: Not found")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Scraping completed! Data saved to '{output_dir}/'")

if __name__ == "__main__":
    scrape_data()