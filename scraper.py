import requests
from bs4 import BeautifulSoup

class Matches:
    @staticmethod
    def _get_page_content(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    @staticmethod
    def match_schedule():
        URL = 'https://www.vlr.gg/matches'
        soup = Matches._get_page_content(URL)

        schedule = soup.find('div', class_='col mod-1')
        dates = schedule.find_all('div', class_='wf-label')
        cards = schedule.find_all('div', class_='wf-card')

        matches_list = []
        for key, value in zip(dates, cards):
            match_items = value.find_all('a', class_='match-item')
            for match_item in match_items:
                match_data = Matches._extract_match_data(match_item)
                matches_list.append({'date': key.get_text(strip=True), **match_data})

        return matches_list

    @staticmethod
    def _extract_team_data(team_item):
        team_data = {
            'name': team_item.find('div', class_='match-item-vs-team-name').get_text(strip=True),
            'score': team_item.find('div', class_='match-item-vs-team-score').get_text(strip=True),
        }

        return team_data

    @staticmethod
    def _extract_match_data(match_item):
        match_data = {
            'time': match_item.find('div', class_='match-item-time').get_text(strip=True),
            'teams': [],
            'status': match_item.find('div', class_='ml-status').get_text(strip=True),
            'eta': match_item.find('div', class_='match-item-eta').get_text(strip=True),
            'tournament_img': match_item.find('img')['src'],  # Add tournament image URL
            'tournament_name': match_item.find('div', class_='match-item-event-series').get_text(strip=True),
            # Add tournament name
            'tournament_stage': match_item.find('div', class_='match-item-event').get_text(strip=True).replace(
                match_item.find('div', class_='match-item-event-series').get_text(strip=True), '').strip(),
            # Add modified tournament stage
        }

        team_items = match_item.find_all('div', class_='match-item-vs-team')
        for team_item in team_items:
            team_data = Matches._extract_team_data(team_item)
            match_data['teams'].append(team_data)

        # Extract match_link from the 'href' attribute
        match_data['link'] = match_item['href']

        return match_data

    @staticmethod
    def extract_team_logos(match_links):
        base_url = 'https://www.vlr.gg'
        team_logos = {}

        for match_link in match_links:
            full_url = base_url + match_link
            soup = Matches._get_page_content(full_url)

            team_logo_divs_mod1 = soup.find_all('a', class_='match-header-link wf-link-hover mod-1')
            team_logo_divs_mod2 = soup.find_all('a', class_='match-header-link wf-link-hover mod-2')

            for team_div in team_logo_divs_mod1 + team_logo_divs_mod2:
                team_name = team_div.find('div', class_='wf-title-med').get_text(strip=True)
                team_logo_url = team_div.find('img')['src']

                # Store team logos as dictionaries
                team_logos[team_name] = {'logo': team_logo_url}

        return team_logos

    @staticmethod
    def api_ready_match_schedule():
        schedule = Matches.match_schedule()
        match_links = [match_data['link'] for match_data in schedule]
        team_logos = Matches.extract_team_logos(match_links)

        # Filter out matches with TBD teams
        schedule = [match_data for match_data in schedule if
                    not any(team_data['name'] == 'TBD' for team_data in match_data['teams'])]

        for match_data in schedule:
            for team_data in match_data['teams']:
                team_name = team_data['name']
                if team_name in team_logos:
                    # Make sure team_logos[team_name] is a dictionary
                    team_data['logo'] = team_logos[team_name].get('logo', '')

        return schedule