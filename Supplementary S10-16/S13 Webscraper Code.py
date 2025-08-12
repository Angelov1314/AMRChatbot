import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import time
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import openai
import json

# Load API keys from config file
with open('../api_keys.json', 'r') as f:
    api_keys = json.load(f)

def sanitize_filename(filename):
    # Remove or replace invalid filename characters
    # Keep only alphanumeric characters, dashes, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9-_]', '_', filename)
    # Ensure the filename isn't too long
    return sanitized[:100]  # Limit to 100 characters

def parse_chat_table(html):
    soup = BeautifulSoup(html, "html.parser")
    # Find all tables with the chat-table ID (in case of multiple tables)
    tables = soup.find_all("table", {"id": "chat-table"})
    
    data = []
    for table in tables:
        tbody = table.find("tbody")
        if tbody:
            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                # Get text from each cell, stripping whitespace and getting text from spans if present
                values = []
                for cell in cells:
                    # If there's a span, get its text, else get cell text
                    span = cell.find("span")
                    if span:
                        values.append(span.get_text(strip=True))
                    else:
                        values.append(cell.get_text(strip=True))
                # Map to column names
                if len(values) >= 4:  # Ensure we have enough columns
                    data.append({
                        "date_time": values[0],
                        "role": values[1],
                        "message_content": values[3],
                    })
    
    print(f"Found {len(tables)} tables, extracted {len(data)} rows total")
    return data

def process_conversation_with_gpt(conversation_data, client):
    """Process conversation data through GPT to extract structured information"""
    try:
        # Convert conversation data to JSON string
        data_str = json.dumps(conversation_data, ensure_ascii=False, indent=2)
        
        prompt = f"""Here is a chat log in JSON format: {data_str}

Please analyze this conversation of a human and a chatbot, where the chatbot is trying to collect antimicrobial resistance data from the human, while the human might ask unrelated questions to the chatbot.

Extract the relevant information and return ONLY a single CSV data row (no header) with the following 15 values in this exact order:
1. Email address - extract the actual email address mentioned
2. Date of interview - extract the actual date when the conversation took place
3. Symptoms - extract the actual symptoms mentioned (e.g., "fever, cough, headache")
4. Are you taking any medication today? - extract the actual answer (Yes/No)
5. Medication name/label - extract the exact drug name from any medication images mentioned (e.g., "Paracetamol 500mg", "Amoxicillin 250mg", "Ibuprofen 200mg"). If the image shows a specific drug, extract that exact name. Do not use generic terms like "no identifiable antibiotic drug".
6. Source of medicine - extract where they got the medicine (e.g., "pharmacy", "hospital", "friend")
7. Have prescription - extract if they have a prescription (Yes/No)
8. Medication duration - extract how long they've been taking it (e.g., "3 days", "1 week")
9. Do you think the medicine which you are currently taking contains antibiotics - extract their answer (Yes/No/Don't know)
10. Medication name/label 2 - extract the exact drug name from any second medication images mentioned (e.g., "Erythromycin 250mg", "Ciprofloxacin 500mg"). If the image shows a specific drug, extract that exact name. Do not use generic terms like "no identifiable antibiotic drug".
11. Source of medicine 2 - extract where they got the second medicine
12. Have prescription 2 - extract if they have a prescription for the second medicine (Yes/No)
13. Medication duration 2 - extract how long they've been taking the second medicine
14. Length of survey - extract how long the survey took (e.g., "5 minutes", "10 minutes")
15. Suggestion - extract any suggestions or feedback mentioned

Return ONLY the actual data values separated by commas, with no header row. If a field has no data, use "No data". If a field contains commas, wrap it in quotes.

IMPORTANT: Return the actual extracted data, not numbers or placeholders. For example, if they mention "fever and cough", return "fever and cough", not "1" or "symptoms".

CRITICAL: For medication fields, extract the EXACT drug name from the images (e.g., "Paracetamol 500mg", "Amoxicillin 250mg", "Ibuprofen 200mg"). Do NOT use generic terms like "no identifiable antibiotic drug" or "unknown medication". If you can see a drug name in the image, extract that specific name.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant that analyzes conversations and extracts structured information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10000
        )
        
        csv_text = response.choices[0].message.content.strip()
        print(f"GPT Response: {csv_text}")
        
        # Parse the CSV response
        lines = csv_text.splitlines()
        print(f"Number of lines in response: {len(lines)}")
        
        # Find the first non-empty line that contains data
        data_line = None
        for line in lines:
            line = line.strip()
            if line and not line.startswith("Date of interview") and "," in line:
                data_line = line
                break
        
        if data_line:
            print(f"Found data line: {data_line}")
            
            # Use proper CSV parsing to handle commas within fields
            import csv
            from io import StringIO
            
            # Create a CSV reader to properly parse the data row
            csv_reader = csv.reader(StringIO(data_line))
            values = next(csv_reader)  # Get the first (and only) row
            values = [val.strip().strip('"') for val in values]
            print(f"Parsed values: {values}")
            print(f"Number of values: {len(values)}")
            
            # Validate that we have the expected number of values (15)
            if len(values) != 15:
                print(f"Warning: Expected 15 values, but got {len(values)}")
                # Pad with empty strings if we have fewer values
                while len(values) < 15:
                    values.append("")
                # Truncate if we have more values
                values = values[:15]
            
            # Create structured data dictionary
            structured_data = {
                "Email address": values[0] if len(values) > 0 else "",
                "Date of interview": values[1] if len(values) > 1 else "",
                "Symptoms": values[2] if len(values) > 2 else "",
                "Are you taking any medication today?": values[3] if len(values) > 3 else "",
                "Medication photo": values[4] if len(values) > 4 else "",
                "Source of medicine": values[5] if len(values) > 5 else "",
                "Have prescription": values[6] if len(values) > 6 else "",
                "Medication duration": values[7] if len(values) > 7 else "",
                "Do you think the medicine which you are currently taking contains antibiotics": values[8] if len(values) > 8 else "",
                "Medication photo 2": values[9] if len(values) > 9 else "",
                "Source of medicine 2": values[10] if len(values) > 10 else "",
                "Have prescription 2": values[11] if len(values) > 11 else "",
                "Medication duration 2": values[12] if len(values) > 12 else "",
                "Length of survey": values[13] if len(values) > 13 else "",
                "Suggestion": values[14] if len(values) > 14 else ""
            }
            
            print(f"Structured data created: {structured_data}")
            
            return structured_data
        else:
            print("Invalid CSV response from GPT")
            return None
            
    except Exception as e:
        print(f"Error processing conversation with GPT: {str(e)}")
        return None

# Set maximum number of URLs to collect
MAX_URLS = 2  # Scrape 20 conversations at once

# Set up the folder to save logs
output_folder = "Data/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_keys['openai_api_key'])

# Set up Selenium with Chrome
driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
driver.maximize_window()

try:
    # Step 1: Navigate to Chatbean login page
    driver.get("https://chatbean.co/login")
    time.sleep(2)

    # Handle the cookie consent popup
    try:
        accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all cookies')]"))
        )
        accept_cookies_button.click()
        time.sleep(1)
    except TimeoutException:
        print("Cookie consent popup not found within 10 seconds.")

    # Log in
    email_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "email"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
    time.sleep(1)
    email_field.send_keys(api_keys['chatbean_email'])  # Use API key from config

    password_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
    time.sleep(1)
    password_field.send_keys(api_keys['chatbean_password'])  # Use API key from config

    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    sign_in_button.click()
    time.sleep(5)

    # Step 2: Redirect to the specified logs URL
    logs_url = "https://chatbean.co/logs/2cbb466a-37ff-418a-a6f2-a72335de4e1b"
    driver.get(logs_url)
    time.sleep(3)

    # Step 3: Find all hyperlinks and store in a dictionary
    log_links_dict = {}  # Dictionary to store hyperlinks and their message content
    processed_hrefs = set()  # Track processed links to avoid duplicates

    while True:
        try:
            # Check if we've reached the maximum number of URLs
            if len(processed_hrefs) >= MAX_URLS:
                print(f"Reached maximum limit of {MAX_URLS} URLs. Stopping collection.")
                break

            # Find all hyperlinks starting with "https://chatbean.co/logs/detail/"
            log_links = driver.find_elements(
                By.XPATH, "//a[starts-with(@href, 'https://chatbean.co/logs/detail/')]"
            )

            # If no links found, break
            if not log_links:
                print("No hyperlinks starting with 'https://chatbean.co/logs/detail/' found on this page.")
                with open(os.path.join(output_folder, "logs_page_source.html"), "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved page source to {output_folder}/logs_page_source.html for debugging.")
                break

            # Debug: Print number of links found
            print(f"Found {len(log_links)} hyperlinks starting with 'https://chatbean.co/logs/detail/' on the page.")

            # Add unprocessed links to the dictionary
            for link in log_links:
                href = link.get_attribute("href")
                if href not in processed_hrefs:
                    # Print the element's outerHTML
                    element_html = driver.execute_script("return arguments[0].outerHTML;", link)
                    print(f"Recorded link element: {element_html}")
                    log_links_dict[href] = {"messages": [], "element": link}
                    processed_hrefs.add(href)
                    
                    # Check if we've reached the maximum number of URLs
                    if len(processed_hrefs) >= MAX_URLS:
                        print(f"Reached maximum limit of {MAX_URLS} URLs. Stopping collection.")
                        break

            # If we've reached the maximum, break out of the loop
            if len(processed_hrefs) >= MAX_URLS:
                break

            # Check for pagination
            try:
                next_page = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
                )
                next_page.click()
                time.sleep(3)
                continue
            except TimeoutException:
                print("No 'Next' page found, moving to extraction.")
                break

        except (TimeoutException) as e:
            print(f"Error finding links: {str(e)}")
            continue

    # Step 4: Access each hyperlink and extract data from all pages
    all_logs_data = []
    structured_data_list = []  # List to store GPT-processed structured data
    
    for href in log_links_dict.keys():
        try:
            # Get the base URL without any page parameters
            parsed_url = urlparse(href)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            # Initialize combined HTML for this conversation
            combined_table_html = ""
            
            # Directly scrape 3 pages for each conversation
            for page in range(1, 4):  # Pages 1, 2, 3
                # Construct URL with page parameter
                current_url = f"{base_url}?page={page}" if page > 1 else base_url
                print(f"Navigating to conversation URL: {current_url}")
                driver.get(current_url)
                time.sleep(5)  # Increased wait time for dynamic loading

                # Wait for the table's parent container
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'relative overflow-x-auto')]")
                        )
                    )
                    print("Table container found, page appears to be loaded.")
                except TimeoutException:
                    print(f"Table container not found for {current_url}, saving page source for debugging...")
                    safe_filename = sanitize_filename(f"conversation_{href.split('/')[-2]}_page_{page}_source.html")
                    with open(os.path.join(output_folder, safe_filename), "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"Saved page source to {output_folder}/{safe_filename}")
                    break  # Stop pagination if container not found

                # Find the table
                try:
                    table = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//table[contains(@class, 'w-full text-sm text-left text-gray-500 dark:text-gray-400')]")
                        )
                    )
                except TimeoutException:
                    print(f"Table not found with primary selector for {current_url}, trying fallback selector...")
                    try:
                        table = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//table[@id='chat-table']")
                            )
                        )
                    except TimeoutException:
                        print(f"Table still not found for {current_url}, saving page source for debugging...")
                        safe_filename = sanitize_filename(f"conversation_{href.split('/')[-2]}_page_{page}_source.html")
                        with open(os.path.join(output_folder, safe_filename), "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        print(f"Saved page source to {output_folder}/{safe_filename}")
                        break  # Stop pagination if table not found

                # Extract the full HTML of the table
                table_html = driver.execute_script("return arguments[0].outerHTML;", table)
                
                # Check if this page has any actual data
                soup = BeautifulSoup(table_html, "html.parser")
                rows = soup.find("tbody")
                if rows and rows.find_all("tr"):
                    combined_table_html += table_html
                    print(f"Successfully extracted table HTML from page {page} with {len(rows.find_all('tr'))} rows")
                else:
                    print(f"Page {page} has no data rows, continuing to next page")
                    continue

            print(f"\nProcessing conversation for {base_url} (pages 1-3) with GPT...")
            print(f"Combined HTML length: {len(combined_table_html)} characters")
            
            # Parse the combined table HTML
            conversation_data = parse_chat_table(combined_table_html)
            print(f"Total conversation entries extracted: {len(conversation_data)}")
            
            # Debug: Show first few entries
            if conversation_data:
                print(f"First entry: {conversation_data[0]}")
                print(f"Last entry: {conversation_data[-1]}")
            
            all_logs_data.append(conversation_data)
            
            # Process conversation through GPT
            structured_data = process_conversation_with_gpt(conversation_data, client)
            if structured_data:
                structured_data_list.append(structured_data)
                print(f"Successfully processed conversation through GPT")
            else:
                print(f"Failed to process conversation through GPT")

            # Go back to the logs list
            driver.get(logs_url)
            time.sleep(3)

        except (TimeoutException) as e:
            print(f"Error processing link {href}: {str(e)}")
            driver.get(logs_url)  # Go back to logs list on error
            time.sleep(3)
            continue

    # Save structured data to CSV file
    if structured_data_list:
        csv_filename = os.path.join(output_folder, "structured_conversations.csv")
        
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(csv_filename)
        
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                "Email address", "Date of interview", "Symptoms", "Are you taking any medication today?",
                "Medication photo", "Source of medicine", "Have prescription", "Medication duration",
                "Do you think the medicine which you are currently taking contains antibiotics",
                "Medication photo 2", "Source of medicine 2", "Have prescription 2", "Medication duration 2",
                "Length of survey", "Suggestion"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Only write header if file doesn't exist (first run)
            if not file_exists:
                writer.writeheader()
            
            for structured_data in structured_data_list:
                writer.writerow(structured_data)
        
        if file_exists:
            print(f"\nNew structured conversations appended to: {csv_filename}")
        else:
            print(f"\nStructured conversations saved to: {csv_filename}")
        print(f"Total conversations processed: {len(all_logs_data)}")
        print(f"Total conversations successfully structured: {len(structured_data_list)}")
    else:
        print("\nNo structured data was generated successfully.")

    # Also save raw conversation data for reference (overwrite each time)
    if all_logs_data:
        raw_csv_filename = os.path.join(output_folder, "raw_conversations.csv")
        
        with open(raw_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date_time', 'role', 'message_content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for conversation_data in all_logs_data:
                for row in conversation_data:
                    writer.writerow(row)
        
        print(f"Raw conversations saved to: {raw_csv_filename}")

finally:
    driver.quit()
    print("Script completed.") 