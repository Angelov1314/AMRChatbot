import json
import requests

def make_redcap_api_call():
    """Make a REDCap API call using the API keys from the JSON file"""
    
    # Load API keys
    with open('../api_keys.json', 'r') as f:
        api_keys = json.load(f)
    
    # API endpoint
    url = "https://redcap.medsci.ox.ac.uk/redcap_v14.5.34/api/"
    
    # Prepare the data
    data = {
        'token': api_keys['redcap_token'],
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'data': '[{"record_id":"456789"}]'
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    try:
        # Make the API request
        response = requests.post(url, data=data, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("API Response:")
            print(response.json())
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error making API request: {e}")

if __name__ == "__main__":
    make_redcap_api_call() 