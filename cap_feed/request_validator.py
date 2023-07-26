import json

import requests
from bs4 import BeautifulSoup

def get_parsed_html(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # Get the HTML content (body) of the response
            html_content = response.text

            # Parse the HTML content using BeautifulSoup
            parsed_html = BeautifulSoup(html_content, 'html.parser')
            # Get the text content from the parsed HTML
            text_content = parsed_html.get_text()
            json_data = json.loads(text_content)
            # Process the parsed HTML as needed
            # For example, extract specific information or navigate the DOM tree
            print(json_data)
            return parsed_html

        else:
            print(f"Error: Request failed with status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Example usage: Replace 'your_url_here' with the actual URL
url = "http://localhost:8000/get_alerts"
get_parsed_html(url)