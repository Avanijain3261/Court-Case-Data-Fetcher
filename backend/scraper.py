import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
import json
import time
import re

# --- Configuration ---
BASE_URL = "https://delhihighcourt.nic.in"
SEARCH_PAGE_URL = f"{BASE_URL}/app/get-case-type-status"

def scrape_order_details(session: requests.Session, orders_page_url: str) -> list:
    """
    Visits the orders page and scrapes the date and PDF link for each order.
    """
    if not orders_page_url or orders_page_url == "Not found":
        return []

    print("   -> Scraping individual orders from:", orders_page_url)
    try:
        orders_page_response = session.get(orders_page_url)
        orders_page_response.raise_for_status()
        
        with open("orders_page.html", "w", encoding="utf-8") as f:
            f.write(orders_page_response.text)
        print("   -> DEBUG: Saved orders page HTML to 'orders_page.html'")

        soup = BeautifulSoup(orders_page_response.text, 'html.parser')
        
        order_list = []
        # CORRECTED: Find the table by its ID, which is likely 'caseTable' based on the 'aria-describedby' attribute.
        order_table = soup.find('table', id='caseTable')
        if not order_table:
            print("   -> ERROR: Could not find the orders table with id='caseTable'.")
            return []

        order_table_body = order_table.find('tbody')
        if not order_table_body:
            print("   -> ERROR: Could not find the 'tbody' of the orders table.")
            return []

        for row in order_table_body.find_all('tr'):
            cells = row.find_all('td')
            # As per your screenshot, the link is in the 2nd cell (index 1) and date is in the 3rd cell (index 2)
            if len(cells) > 2:
                pdf_link_tag = cells[1].find('a')
                order_date = cells[2].get_text(strip=True)
                
                if pdf_link_tag and pdf_link_tag.has_attr('href'):
                    # The href is a full URL, so we don't need to join it with the base.
                    pdf_url = pdf_link_tag['href']
                    order_list.append({"date": order_date, "url": pdf_url})
        
        print(f"   -> Found {len(order_list)} orders.")
        return order_list

    except requests.exceptions.RequestException as e:
        print(f"   -> ERROR: Could not scrape orders page. {e}")
        return []


def parse_case_data(session: requests.Session, case_json: dict) -> dict:
    """
    Parses the raw JSON data for a single case and extracts clean information.
    """
    if not case_json:
        return {}

    pet_html = BeautifulSoup(case_json.get('pet', ''), 'html.parser')
    party_names = pet_html.get_text(separator=' ', strip=True)

    order_date_text = case_json.get('orderdate', '')
    next_hearing_date = "Not found"
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', order_date_text)
    if date_match:
        next_hearing_date = date_match.group(0)

    ctype_html = BeautifulSoup(case_json.get('ctype', ''), 'html.parser')
    orders_link_tag = ctype_html.find('a', string='Orders')
    orders_page_link = "Not found"
    if orders_link_tag and orders_link_tag.has_attr('href'):
        orders_page_link = urljoin(BASE_URL, orders_link_tag['href'])

    filing_year = case_json.get('cyear', 'N/A')
    filing_date_display = f"Year: {filing_year}"

    orders = scrape_order_details(session, orders_page_link)

    return {
        "party_names": party_names,
        "filing_date": filing_date_display,
        "next_hearing_date": next_hearing_date,
        "orders_link": orders_page_link,
        "orders": orders
    }


def fetch_case_details(case_type: str, case_number: str, case_year: str):
    """
    Fetches and parses case details, including individual order PDFs.
    """
    try:
        with requests.Session() as session:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            print(f"1. Accessing search page to get cookies: {SEARCH_PAGE_URL}")
            page_response = session.get(SEARCH_PAGE_URL)
            page_response.raise_for_status()
            print("   - Search page accessed successfully.")

            xsrf_token = session.cookies.get('XSRF-TOKEN')
            if not xsrf_token:
                print("   - CRITICAL ERROR: Could not find the 'XSRF-TOKEN' cookie.")
                return None
            decoded_xsrf_token = unquote(xsrf_token)
            print("2. Found 'XSRF-TOKEN' cookie.")

            params = {
                'draw': '2',
                'start': '0',
                'length': '50',
                'search[value]': '',
                'search[regex]': 'false',
                'case_type': case_type,
                'case_number': case_number,
                'case_year': case_year,
                '_': int(time.time() * 1000)
            }
            
            headers = {
                'Referer': SEARCH_PAGE_URL,
                'X-XSRF-TOKEN': decoded_xsrf_token,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            print(f"3. Sending GET request to: {SEARCH_PAGE_URL}")
            
            search_response = session.get(SEARCH_PAGE_URL, params=params, headers=headers)
            search_response.raise_for_status()
            
            print("4. Request successful! Processing response...")
            raw_data = search_response.json()
            
            if raw_data.get('data'):
                case_info_json = raw_data['data'][0]
                parsed_data = parse_case_data(session, case_info_json)
                return parsed_data
            else:
                print("   - No case data found in the response.")
                return None

    except requests.exceptions.RequestException as e:
        print(f"\n--- AN ERROR OCCURRED ---")
        print(f"Error: {e}")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text[:500]}...")
        return None