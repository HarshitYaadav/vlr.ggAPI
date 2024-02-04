from bs4 import BeautifulSoup
import requests
#roster
class CombinedStats:
    def __init__(self, match_url):
        self.match_url = match_url

    def _get_page_content(self):
        full_url = f'https://www.vlr.gg{self.match_url}'
        page = requests.get(full_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def clean_date(self, raw_date):
        # Implement your date cleaning logic here
        # For now, let's assume the raw date is already clean
        return raw_date

    def clean_time(self, raw_time):
        # Implement your time cleaning logic here
        # For now, let's assume the raw time is already clean
        return raw_time

    
    @property
    def extract_stats(self):
        try:
            soup = self._get_page_content()

            # Extract tournament information
            tournament_info = soup.find('div', class_='match-header-event-series')
            if tournament_info:
                tournament_name_element = tournament_info.find_previous('div', style='font-weight: 700;')
                tournament_name = tournament_name_element.get_text(strip=True) if tournament_name_element else "N/A"
                tournament_stage = tournament_info.get_text(strip=True).replace(tournament_name, '').strip()
            else:
                print(f"Failed to find tournament information for {self.match_url}")
                return None

            # Extract date and time information
            date_time_container = soup.find('div', class_='match-header-date')
            if date_time_container:
                match_date_element = date_time_container.find('div', class_='moment-tz-convert')
                match_date_raw = match_date_element.get_text(strip=True) if match_date_element else "N/A"
                match_date = self.clean_date(match_date_raw)

                match_time_element = date_time_container.find('div', style='font-size: 12px;')
                match_time = self.clean_time(match_time_element.get_text(strip=True)) if match_time_element else "N/A"
            else:
                print(f"Failed to find date and time information for {self.match_url}")
                return None

            # Extract team information and scores
            team_elements = soup.find_all('a', class_='match-header-link')

            if len(team_elements) == 2:
                team1_name = team_elements[0].find('div', class_='wf-title-med').get_text(strip=True)
                team1_logo_url = team_elements[0].find('img')['src']
                team1_score_element = soup.find('span', class_='match-header-vs-score-winner')
                team1_score = team1_score_element.get_text(strip=True) if team1_score_element else "Scheduled"
                team1_link = team_elements[0]['href']

                team2_name = team_elements[1].find('div', class_='wf-title-med').get_text(strip=True)
                team2_logo_url = team_elements[1].find('img')['src']
                team2_score_element = soup.find('span', class_='match-header-vs-score-loser')
                team2_score = team2_score_element.get_text(strip=True) if team2_score_element else "Scheduled"
                team2_link = team_elements[1]['href']
            else:
                print(f"Failed to find information for Team 1 and Team 2")
                return None

            # Extract time to start the match if scores are not available
            if team1_score == "Scheduled" and team2_score == "Scheduled":
                time_to_start_element = soup.find('span', class_='match-header-vs-note mod-upcoming')
                time_to_start = time_to_start_element.get_text(strip=True) if time_to_start_element else "N/A"
            else:
                time_to_start = "N/A"

            # Extract other details
            match_note = soup.find('div', class_='match-header-note').get_text(strip=True) if soup.find('div', class_='match-header-note') else "N/A"


            self.stats_data = {
                "tournament_name": tournament_name,
                "tournament_stage": tournament_stage,
                "match_url":self.match_url,
                "match_date": match_date,
                "match_time": match_time,
                "time_to_start": time_to_start,
                "team1_name": team1_name,
                "team1_score": team1_score,
                "team1_logo_url": team1_logo_url,
                "team1_cost": 00,  # Initial value for team cost
                "team1_roster": self.extract_roster(team1_link),

                "team2_name": team2_name,
                "team2_score": team2_score,
                "team2_logo_url": team2_logo_url,
                "team2_cost": 00,  # Initial value for team cost
                "team2_roster": self.extract_roster(team2_link),
                "match_note": match_note,

            }

        except Exception as e:
            print(f"An error occurred: {e}")

    def extract_roster(self, team_link):
        roster_data = []
        try:
            roster_url = f'https://www.vlr.gg{team_link}/roster'
            roster_page = requests.get(roster_url)
            roster_soup = BeautifulSoup(roster_page.content, 'html.parser')

            roster_items = roster_soup.find_all('div', class_='team-roster-item')
            for item in roster_items:
                # Check if the player has a role, indicating staff
                role_element = item.find('div', class_='team-roster-item-name-role')
                if role_element:
                    continue  # Skip staff members

                player_name_element = item.find('div', class_='team-roster-item-name-alias')
                player_name = player_name_element.get_text(strip=True) if player_name_element else "N/A"

                player_img_element = item.find('img')
                player_img_url = player_img_element['src'] if player_img_element else "N/A"

                player_url_element = item.find('a', href=True)
                player_url = player_url_element['href'] if player_url_element else "N/A"

                player_info = {
                    "player_name": player_name,
                    "player_cost": 00,  # Initial value for player cost
                    "player_img_url": player_img_url,
                    "player_url": player_url,
                }
                roster_data.append(player_info)

        except Exception as e:
            print(f"An error occurred while extracting roster: {e}")

        return roster_data

    def extract_combined_stats(self):
        # Call extract_stats from MatchStats
        self.extract_stats
        return self.stats_data


