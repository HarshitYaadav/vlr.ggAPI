import requests
from bs4 import BeautifulSoup
import json


class PlayerScraper:
    def __init__(self, url):
        self.url = url

    def scrape_event_data(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        teams = []

        # Extract team information
        team_cards = soup.find_all('div', class_='wf-card event-team')
        for team_card in team_cards:
            team_info = {}
            team_info['name'] = team_card.find('a', class_='event-team-name').text.strip()
            team_info['url'] = 'https://www.vlr.gg' + team_card.find('a', class_='event-team-name')['href']
            team_info['logo'] = team_card.find('img', class_='event-team-players-mask-team')['src']
            teams.append(team_info)

        # Extract player rosters
        for team_info in teams:
            response_team = requests.get(team_info['url'])
            soup_team = BeautifulSoup(response_team.content, 'html.parser')

            players = []
            player_items = soup_team.find_all('div', class_='team-roster-item')
            for player_item in player_items:
                # Check if the entry represents a staff member
                is_staff = player_item.find('div', class_='team-roster-item-name-role') is not None

                # Check if the entry represents a sub-player
                is_sub = 'Sub' in player_item.find('div', class_='team-roster-item-name-role').text if player_item.find(
                    'div', class_='team-roster-item-name-role') else False

                # Include the entry if it's not a staff member
                if not is_staff or is_sub:
                    player = {}
                    player['name'] = player_item.find('div', class_='team-roster-item-name-alias').text.strip()

                    # Check if 'team-roster-item-name-real' element exists before accessing its text
                    real_name_element = player_item.find('div', class_='team-roster-item-name-real')
                    player['real_name'] = real_name_element.text.strip() if real_name_element else ''

                    player['image'] = player_item.find('img')['src']
                    player['url'] = 'https://www.vlr.gg' + player_item.find('a')['href']

                    # Add display attribute with default value 0
                    player['display'] = 0

                    players.append(player)

            team_info['players'] = players

        return {"event-player-list": teams}


# Example usage
if __name__ == "__main__":
    event_url = 'https://www.vlr.gg/event/1924/champions-tour-2024-pacific-kickoff'
    player_scraper = PlayerScraper(event_url)
    event_data = player_scraper.scrape_event_data()
    print(json.dumps(event_data, indent=2))
