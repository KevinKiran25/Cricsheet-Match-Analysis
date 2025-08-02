import os
import time
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

#Define Download Directory
download_dir = os.path.abspath("data")
os.makedirs(download_dir, exist_ok=True)

#Define Required Match Files
required_match_files = {
    "tests_json.zip": "https://cricsheet.org/downloads/tests_json.zip",
    "odis_json.zip": "https://cricsheet.org/downloads/odis_json.zip",
    "t20s_json.zip": "https://cricsheet.org/downloads/t20s_json.zip",
    "ipl_json.zip": "https://cricsheet.org/downloads/ipl_json.zip",
}

#Faster Download Using `requests`
def download_file(url, filename):
    file_path = os.path.join(download_dir, filename)
    if os.path.exists(file_path):
        print(f"Already downloaded: {filename}")
        return

    response = requests.get(url, stream=True)
    
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            file.write(chunk)

    print(f"Downloaded: {filename}")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://cricsheet.org/downloads/")
time.sleep(3)  
driver.quit()  

for filename, url in required_match_files.items():
    download_file(url, filename)

zip_files = [f for f in os.listdir(download_dir) if f.endswith(".zip")]
for zip_file in zip_files:
    zip_path = os.path.join(download_dir, zip_file)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(download_dir)
    print(f"Extracted: {zip_file}")

print("All JSON files downloaded & extracted successfully!")