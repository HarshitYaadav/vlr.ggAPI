import requests
from bs4 import BeautifulSoup

class MatchStats:

    @staticmethod
    def extract_player_image_url(player_page_url):
        response = requests.get(player_page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            player_image_elem = soup.find('div', class_='wf-avatar mod-player').find('img')
            player_image_url = player_image_elem['src'] if player_image_elem else "Player Image URL Not Found"
            return player_image_url
        else:
            return "Failed to retrieve player page. Status code: {}".format(response.status_code)

    @staticmethod
    def get_match_stats(match_url):
        response = requests.get(match_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            maps_container = soup.find('div', class_='vm-stats-gamesnav-container')
            map_items = maps_container.find_all('div', class_='vm-stats-gamesnav-item')

            maps_info = []
            for map_item in map_items:
                map_id = map_item['data-game-id']
                map_number_elem = map_item.find('span', style='vertical-align: 4px; font-weight: 400;')
                map_number = map_number_elem.text.strip() if map_number_elem else "Map Number Not Found"

                map_details_div = soup.find('div', class_='vm-stats-game', attrs={'data-game-id': map_id})

                if map_details_div:
                    map_name_elem = map_details_div.select_one(
                        '.vm-stats-game-header .map div[style*="font-weight: 700;"] span[style*="position: relative"]')
                    map_name = map_name_elem.get_text(strip=True).replace("PICK", "") if map_name_elem else "Map Name Not Found"
                else:
                    map_name = "Map Name Not Found"

                maps_info.append({
                    'map_id': map_id,
                    'map_number': map_number,
                    'map_name': map_name,
                    'team1_name': "",
                    'team1_score': "",
                    'team2_name': "",
                    'team2_score': "",
                    'players': []
                })

            for map_info in maps_info:
                map_id = map_info['map_id']
                game_stats_div = soup.find('div', class_='vm-stats-game', attrs={'data-game-id': map_id})

                if game_stats_div:
                    team1_name_elem = game_stats_div.find('div', class_='team-name')
                    team1_name = team1_name_elem.text.strip() if team1_name_elem else "Team 1 Name Not Found"

                    team1_score_elem = game_stats_div.find('div', class_='team')
                    team1_score = team1_score_elem.find('div',
                                                        class_='score').text.strip() if team1_score_elem and team1_score_elem.find(
                        'div', class_='score') else "Team 1 Score Not Found"

                    team2_name_elem = game_stats_div.find('div', class_='team mod-right')
                    team2_name = team2_name_elem.find('div',
                                                      class_='team-name').text.strip() if team2_name_elem and team2_name_elem.find(
                        'div', class_='team-name') else "Team 2 Name Not Found"

                    team2_score_elem = game_stats_div.find('div', class_='team mod-right')
                    team2_score = team2_score_elem.find('div',
                                                        class_='score').text.strip() if team2_score_elem and team2_score_elem.find(
                        'div', class_='score') else "Team 2 Score Not Found"

                    map_info['team1_name'] = team1_name
                    map_info['team1_score'] = team1_score
                    map_info['team2_name'] = team2_name
                    map_info['team2_score'] = team2_score

                    player_stats_rows = game_stats_div.select('tbody tr')

                    for player_row in player_stats_rows:
                        player_name_elem = player_row.find('td', class_='mod-player').find('div', class_='text-of')
                        player_name = player_name_elem.text.strip() if player_name_elem else "Player Name Not Found"

                        player_team_elem = player_row.find('div', class_='ge-text-light')
                        player_team = player_team_elem.text.strip() if player_team_elem else "Player Team Not Found"

                        stats = player_row.select('td.mod-stat')
                        kills = stats[2].find('span', class_='mod-both').text.strip()
                        deaths = stats[3].find('span', class_='mod-both').text.strip()
                        assists = stats[4].find('span', class_='mod-both').text.strip()

                        player_page_elem = player_row.find('td', class_='mod-player').find('a')
                        player_page_url = "https://www.vlr.gg" + player_page_elem['href'] if player_page_elem else "Player Page URL Not Found"

                        player_image_url = MatchStats.extract_player_image_url(player_page_url)

                        map_info['players'].append({
                            'player_name': player_name,
                            'player_team': player_team,
                            'kills': kills,
                            'deaths': deaths,
                            'assists': assists,
                            'player_image_url': player_image_url
                        })

            return maps_info

        else:
            return None  # Return None if the request fails
