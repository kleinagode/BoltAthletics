import requests
from bs4 import BeautifulSoup
import pandas as pd

class GameStatsScraper:
    def __init__(self, url):
        self.url = url
        self.page = None
        self.soup = None

    def fetch_page(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            self.page = response.content
            self.soup = BeautifulSoup(self.page, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page: {e}")
            self.soup = None

    def extract_table_data(self):
        
        if not self.soup:
            print("No page data to parse.")
            return None
        
        # Find the specific table based on an ID or class
        table = self.soup.find('table', {'id': 'box-score-advanced-florida'})
        if not table:
            print("Could not find the table on the page.")
            return None
        
        # Use pandas to read the HTML table directly into a DataFrame
        df = pd.read_html(str(table))[0]
        return df

    def get_game_stats(self):
        
        self.fetch_page()
        if self.soup:
            return self.extract_table_data()
        else:
            return None
