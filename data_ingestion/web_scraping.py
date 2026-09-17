import requests
from bs4 import BeautifulSoup


def scrape_financial_news(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 
                             'AppleWebKit/537.36 (KHTML, like Gecko)' 
                             'Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = [h.get_text(strip=True) for h in soup.find_all('h3')]
    return headlines


def scrape_economic_indicators(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    indicators = {}
    for td in soup.find_all('tr', class_='row yf-vaowmx'):
        key = td.find('td', class_='label yf-vaowmx').get_text(strip=True)
        value = td.find('td', class_='value yf-vaowmx').get_text(strip=True)
        indicators[key] = value
    return indicators
