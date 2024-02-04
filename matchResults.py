import requests
from bs4 import BeautifulSoup
import time

def get_match_results(url, limit=15):
    # Function to scrape match results from vlr.gg

    # Make a request to the provided URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the match result elements
    match_elements = soup.find_all('a', class_='match-item')

    match_results = []

    for match_element in match_elements:
        # Check if we have reached the desired limit
        if len(match_results) >= limit:
            break

        # Extract information from the match result element
        match_date_raw = soup.find('div', class_='wf-label').text.strip()
        # Clean up the date string
        match_date = match_date_raw.split('\n')[0].strip()

        match_time = match_element.find('div', class_='match-item-time').text.strip()

        team1_name = match_element.find('div', class_='match-item-vs-team-name').text.strip()
        team1_flag = match_element.find('span', class_='flag')['class'][1][4:]  # Extract country code

        team2_name = match_element.find_all('div', class_='match-item-vs-team-name')[1].text.strip()
        team2_flag = match_element.find_all('span', class_='flag')[1]['class'][1][4:]  # Extract country code

        # Extract score information
        team1_score = match_element.find('div', class_='match-item-vs-team-score').text.strip()
        team2_score = match_element.find_all('div', class_='match-item-vs-team-score')[1].text.strip()

        match_link = match_element['href']
        match_url = f'https://vlr.gg{match_link}'

        try:
            # Scraping the match page for team logos
            match_page_response = requests.get(match_url)
            match_page_response.raise_for_status()  # Raise an HTTPError for bad responses
            match_page_soup = BeautifulSoup(match_page_response.content, 'html.parser')

            team1_logo = match_page_soup.find('img', alt=f"{team1_name} team logo")['src']
            team2_logo = match_page_soup.find('img', alt=f"{team2_name} team logo")['src']

            # Append the extracted information to the match_results list
            match_results.append({
                'date': match_date,
                'time': match_time,
                'team1_name': team1_name,
                'team1_logo': team1_logo,
                'team1_score': team1_score,
                'team2_name': team2_name,
                'team2_logo': team2_logo,
                'team2_score': team2_score,
                'match_link': match_link,  # Add the 'match_link' key
            })
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve match page. Error: {e}")

        # Introduce a delay of 1 second between requests
        time.sleep(1)

    return match_results


if __name__ == "__main__":
    url = "https://vlr.gg/matches/results"
    results = get_match_results(url, limit=15)

    if results:
        for result in results:
            print(result)
