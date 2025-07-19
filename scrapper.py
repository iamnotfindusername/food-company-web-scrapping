import requests
from bs4 import BeautifulSoup, Comment
import csv 
import time
import os
import random
from datetime import datetime
from termcolor import colored
import re

def save_contacts_to_csv(contacts, filename=None):
    os.makedirs("data", exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/contacts_{timestamp}.csv"
    else:
        filename = os.path.join("data", filename)

    fieldnames = ['address', 'phones', 'email', 'website']

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for contact in contacts:
            if isinstance(contact.get('phones'), list):
                contact['phones'] = ','.join(contact['phones'])

            writer.writerow(contact)

    print(f"[✓] Data is saved to: {filename}")

def filter_contact_info(data_list):
    phones = []
    email = None
    website = None

    phone_pattern = re.compile(r'^\d{9,15}$')  
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    website_pattern = re.compile(r'^https?://')

    for item in data_list:
        item = item.strip()

        if phone_pattern.match(item):
            phones.append(item)
        elif email_pattern.match(item):
            email = item
        elif website_pattern.match(item):
            website = item

    return {
        "phones": phones,
        "email": email,
        "website": website
    }

def decode_cfemail(cfemail):
    r = int(cfemail[:2], 16)
    email = ''.join([chr(int(cfemail[i:i+2], 16) ^ r) for i in range(2, len(cfemail), 2)])
    return email

def get_random_user_agent(file_path="user_agent.txt"):
    """Selects a random user-agent from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            agents = [line.strip() for line in f if line.strip()]
        return random.choice(agents)
    except FileNotFoundError:
        print(colored("[ERROR] user_agent.txt not found!", "red"))
        return "Mozilla/5.0"

def fetch_page(url, headers):
    """Fetches HTML content from a URL."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # print(colored("[INFO] Page fetched successfully.", "green"))
        return response.text
    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None

def fetch_data(url):
    try:
        user_agent = get_random_user_agent()
        headers = {"User-Agent": user_agent}

        html = fetch_page(url, headers)
        if not html:
            return None 

        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None

def print_progress(current, total, bar_length=40):
    """Prints a progress bar to the terminal."""
    percent = current / total
    filled_length = int(bar_length * percent)
    bar = "█" * filled_length + '-' * (bar_length - filled_length)
    print(f"\r[INFO] Progress: |{bar}| {percent*100:6.2f}% ({current}/{total})", end='')

def extract_href(js_line: str) -> str | None:
    match = re.search(r"window\.location\.href='(.*?)'", js_line)
    return match.group(1) if match else None

def find_page_url(content):
    try:
        span = content.find("span")

        if not span:
            return 

        link = span["onclick"]
        filtered_link = extract_href(link)  

        if not filtered_link:
            return 

        href = "https://www.proveedores.com/" + filtered_link

        return href
    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None

def extract_data(soup):
    try:
        main_content = find_main_content("Main Content", soup)
        contents = main_content.find_all("div", recursive=False) 

        if not contents:
            return

        data = []
        
        for content in contents:
            url = find_page_url(content)

            if not url:
                continue

            soup = fetch_data(url)

            if not soup: 
                continue
            
            ic = soup.find("div", class_="main-content")

            if not ic:
                continue

            contact_information = find_main_content("Contact Information", ic)

            if not contact_information:
                continue    

            address = contact_information.find("p").text
            contact = extract_contact_information(contact_information)
            
            result = {
                        "address":address,
                        **contact
                    }
            data.append(result)

        return data
    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None

def extract_contact_information(soup):
    try:
        ul = soup.find("ul")

        if not ul:
            return
        
        lis = ul.find_all("li")
        
        if not lis:
            return

        result = []

        for li in lis:
            raw_data = li.text
            cleaned_data = re.sub(r'[\s]', '', raw_data)

            if "[emailprotected]" in cleaned_data:
                a = li.find("a")
                cfemail =(a["data-cfemail"])
                email = decode_cfemail(cfemail)
                result.append(email)

            else:
                result.append(cleaned_data)
        
        data = filter_contact_info(result)

        return data 

    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None

def find_main_content(c, soup):
    try:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        for comment in comments:
            if c in comment:
                div = comment.find_next_sibling('div')
                if div:
                    main_content = div.find("div")
                    if not main_content:
                        return None
                    return main_content 
                else:
                    print(colored(f"[WARN] Div not found", "yellow"))

    except requests.RequestException as e:
        print(colored(f"[ERROR] Failed to fetch page: {e}", "red"))
        return None


def main():
    try:
        start_time = time.time()
        total_page = 13 
        data = []

        for page_number in range(1,total_page):
            url = f"https://www.proveedores.com/search?s=Fresas&sev_slug=fresas&sev_id=3809&geo&geo_slug&ae2_id=++++&pop_id&sa=1&tp_id&sb=1&page={page_number}"

            soup = fetch_data(url)

            if not soup:
                return

            exd = extract_data(soup)

            print_progress(page_number, total_page)
            data.extend(exd)

        save_contacts_to_csv(data)

        elapsed = time.time() - start_time

        print(colored(f"[INFO] Scraping complete. Total time: {elapsed:.2f} seconds", "blue"))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
