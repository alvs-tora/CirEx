import os
import time
import platform
import requests
import pdfplumber
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======================
# Setup Directories
# ======================
def setup_directories():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(BASE_DIR, "daily-metal-prices-record")
    os.makedirs(target_dir, exist_ok=True)
    return BASE_DIR, target_dir


# ======================
# OS Detection & WebDriver Setup
# ======================
def get_webdriver():
    system_os = platform.system()
    print(f"Running on: {system_os}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI (safe for RPi or CLI Windows)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Optional: faster page loads
    chrome_options.page_load_strategy = 'eager'

    # Setup WebDriver based on OS
    if system_os == "Windows":
        driver = webdriver.Chrome()

    elif system_os == "Linux":
        chromedriver_path = "/usr/lib/chromium-browser/chromedriver"  # Adjust path if needed
        service = Service(chromedriver_path)
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(service=service, options=chrome_options)

    else:
        raise Exception("Unsupported OS")
    
    return driver


# ======================
# Fetch PDF URL from Web
# ======================
def fetch_pdf_url(driver):
    driver.get("https://mgb.gov.ph/23-industry-statistics/1303-msc-price-watch")
    wait = WebDriverWait(driver, 10)
    metal_price_link_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Daily Metal Price')]")))
    pdf_url = metal_price_link_element.get_attribute('href')
    return pdf_url


# ======================
# Download PDF
# ======================
def download_pdf(pdf_url, target_dir, timestamp):
    file_id = pdf_url.split('/d/')[1].split('/')[0]
    direct_url = f"https://drive.google.com/uc?id={file_id}&export=download"
    pdf_response = requests.get(direct_url)
    output_path = os.path.join(target_dir, f"daily_metal_prices_{timestamp}.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(pdf_response.content)
    print(f"✅ PDF saved to: {output_path}")
    return output_path


# ======================
# Extract and Clean Text from PDF
# ======================
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


# ======================
# Clean and Parse Text
# ======================
def clean_and_parse_text(text):
    cleaned_text = re.sub(r"LEGEND :.*?disclaims any liability.*", "", text, flags=re.DOTALL)
    metals_to_exclude = [
        "Aluminum Alloy", "Rhodium", "Manganese Ore (32%)", "Kruggerand", "Iridium",
        "whs rot", "Chromite Ore", "Manganese (44% Mn)", "Iron Ore (67.5% Fe)"
    ]
    pattern = r"^(.*(?:{}).*)$".format("|".join(map(re.escape, metals_to_exclude)))
    cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r"\s?\(.*?\)", "", cleaned_text)

    remove_words = ["Mineral","Unit","Price","Closing","Source", "BSP", "LME", "T.E. ", "com", "M.B.com", "DMP.com", "*USGS/CRU", "WB", " *USGS/CRU"]
    pattern = r'\b(' + '|'.join(map(re.escape, remove_words)) + r')\b'
    cleaned_text = re.sub(pattern, "", cleaned_text)
    
    # Remove spaces within numbers
    cleaned_text = re.sub(r'(\d)\s(\d)', r'\1\2', cleaned_text)

    # Replace 'troy oz' with 'troyOz' in the unit part
    cleaned_text = re.sub(r'troy\s+oz', 'troyOz', cleaned_text)

    return cleaned_text


# ======================
# Extract Data from Cleaned Text
# ======================
def extract_metal_data(cleaned_text):
    date_pattern = r"^(\w+\s\d{2},\s\d{4})"
    date_match = re.match(date_pattern, cleaned_text)
    date = date_match.group(1) if date_match else "Unknown Date"

    pattern = r"([A-Za-z\s]+)\s+([A-Za-z/]+\S*)\s+([0-9,]+\.\d+)"
    matches = re.findall(pattern, cleaned_text)

    data = {
        "Date": date,
        "Metals": [],
        "Price": [],
        "Unit": []
    }

    for match in matches:
        metal_name = match[0].strip()
        unit = match[1].strip()
        price = float(match[2].replace(",", ""))
        data["Metals"].append(metal_name)
        data["Unit"].append(unit)
        data["Price"].append(price)

    return data


# ======================
# Convert USD to PHP
# ======================
def convert_usd_to_php(usd_prices):
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    rate = response.json()['rates']['PHP']
    php_prices = [round(price * rate, 2) for price in usd_prices]
    return php_prices

def rate():
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    rate = response.json()['rates']['PHP']
    return rate

# ======================
# Convert Units to mg and Prices
# ======================
def convert_to_mg(data):
    unit_to_mg = {
        '₱PESO/oz.': 28349.5,  # regular ounce to milligrams
        '₱PESO/troyOz.': 31103.5,  # troy ounce to milligrams
        '₱PESO/mt': 1e9,  # metric tonne to milligrams
        '₱PESO/Tonne': 1e9,  # tonne to milligrams
        '₱PESO/lb.': 453592.37  # pound to milligrams
    }

    price_mg = []
    for unit, price in zip(data['Unit'], data['Price_PHP']):
        # Check for 'troyOz.' specifically
        if 'troyOz.' in unit:
            mg = unit_to_mg['₱PESO/troyOz.']
        elif 'oz.' in unit:  # Regular ounce check
            mg = unit_to_mg['₱PESO/oz.']
        elif 'mt' in unit:
            mg = unit_to_mg['₱PESO/mt']
        elif 'Tonne' in unit:
            mg = unit_to_mg['₱PESO/Tonne']
        elif 'lb.' in unit:
            mg = unit_to_mg['₱PESO/lb.']
        else:
            mg = 1  # fallback to avoid division by zero if unknown unit
        
        price_per_mg = price / mg
        price_mg.append(round(price_per_mg, 8))

    data['PricePHP_per_mg'] = price_mg
    return data

# ======================
# Main Function
# ======================
def main():
    try:
        # Setup
        base_dir, target_dir = setup_directories()
        timestamp = time.strftime("%d%m%Y")

        # Get WebDriver and fetch PDF URL
        driver = get_webdriver()
        pdf_url = fetch_pdf_url(driver)
        driver.quit()

        # Download the PDF
        pdf_path = download_pdf(pdf_url, target_dir, timestamp)

        # Extract and Clean PDF Text
        text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_and_parse_text(text)

        # Extract Metal Data
        data = extract_metal_data(cleaned_text)

        # Convert USD to PHP
        php_prices = convert_usd_to_php(data["Price"])

        # Add PHP prices to data
        data['Price_PHP'] = php_prices
        
        # Replace "US$" with "₱PESO" in Unit list
        data['Unit'] = [unit.replace("US$", "₱PESO") for unit in data['Unit']]
        data['Price_USD'] = data.pop('Price')

        # Convert to mg and update prices
        data = convert_to_mg(data)
        
        #Convert all metals to lowercase
        data['Metals'] = [metal.lower() for metal in data['Metals']]
        
        #Swap "Iron Ore" and "Chromium" along with their respective values
        iron_index = data['Metals'].index('iron ore')
        chromium_index = data['Metals'].index('chromium')
        
        # Swap the positions in 'Metals', 'Unit', 'Price_PHP', 'Price_USD', and 'PricePHP_per_mg'
        data['Metals'][iron_index], data['Metals'][chromium_index] = data['Metals'][chromium_index], data['Metals'][iron_index]
        data['Unit'][iron_index], data['Unit'][chromium_index] = data['Unit'][chromium_index], data['Unit'][iron_index]
        data['Price_PHP'][iron_index], data['Price_PHP'][chromium_index] = data['Price_PHP'][chromium_index], data['Price_PHP'][iron_index]
        data['Price_USD'][iron_index], data['Price_USD'][chromium_index] = data['Price_USD'][chromium_index], data['Price_USD'][iron_index]
        data['PricePHP_per_mg'][iron_index], data['PricePHP_per_mg'][chromium_index] = data['PricePHP_per_mg'][chromium_index], data['PricePHP_per_mg'][iron_index]

        #Rename "iron ore" to "iron"
        data['Metals'][data['Metals'].index('iron ore')] = 'iron'

        # Convert the data into a DataFrame
        df = pd.DataFrame({
            'Date': [data['Date']] * len(data['Metals']),  # Same date for all rows
            'Metal': data['Metals'],
            'Price_USD': data['Price_USD'],
            'Unit': data['Unit'],
            'Price_PHP': data['Price_PHP'],
            'PricePHP_per_mg': data['PricePHP_per_mg']
        })

        # Save to CSV
        output_file = f'{base_dir}/flat_files/daily_metal_prices.csv'
        df.to_csv(output_file, index=False)
        
        return True
    
    except:
        return False


if __name__ == "__main__":
    main()
