from general_functions import soupify, type_check, table_exists, create_table, insert_data
from general_scrape import EventSearch, PlayerSearch
from dictionaries import event_table_dict, player_table_dict, league_table_dict
import pandas as pd
import itertools
from datetime import date as dt
import re
from statistics import median


class Event(EventSearch):

    def __init__(self, name=None, url=None, year=dt.today().year, tier=['ES', 'M'], classification=['Pro']):

        self.year = int(year)

        if not url:
            self._search_name = name.strip().replace(' ', '%20')
            self._min_date = f'{self.year}-01-01'
            self._max_date = f'{self.year}-12-31'
            self._tier = tier
            self._classification = classification

            self._search_params = {
                'event': self._search_name,
                'date_filter_min': self._min_date,
                'date_filter_max': self._max_date,
                'tier': self._tier,
                'classification': self._classification
            }

            EventSearch.__init__(self, **self._search_params)

        else:
            self.url = url
            self.official_name = name
            self.pdga_event_number = self.url.split('/')[-1]

        # print(self.url)

        self.table_name = self.event_namer()

        self.results_df = self.event_parser(self.url)

        # _exists, _create, _insert = self.sql_queries()

        self.table_exists_query = table_exists(self.table_name)

        self.create_table_query = create_table(self.table_name, event_table_dict())

        # self.insert_values_query = insert_data(
        #     self.table_name,
        #     event_table_dict(),
        #     self.results_df.to_dict('records')
        # )

    def __repr__(self):
        return self.official_name

    def row_parser(self, row):
        if row.select('td[class*="par"]'):
            score = row.select('td[class*="par"]')[0].text
        elif row.select('td[class*="dnf"]'):
            score = "DNF"
        else:
            score = "ERROR"

        try:
            result = {  # could also do round scores, round ratings, and total score
                'EventID': int(self.pdga_event_number),
                'PlayerID': int(row.select_one('td[class*="pdga-number"]').text),
                'Place': int(row.select_one('td[class*="place"]').text),
                'Score': score,
            }

        except:
            result = {}

        return result

    def event_parser(self, url):

        soup = soupify(url)
        soup_table = soup.select('div[class*="leaderboard"]')[0]
        results_table_raw = soup_table.select('div[class*="table-container"]')[0]
        odd_rows = results_table_raw.select('tr[class*="odd"]')
        even_rows = results_table_raw.select('tr[class*="even"]')
        results_raw = [x for x in itertools.chain.from_iterable(itertools.zip_longest(odd_rows, even_rows)) if x]
        results_list = [self.row_parser(row) for row in results_raw if self.row_parser(row)]
        results_df = pd.DataFrame(data=results_list)  # .set_index('Place')

        return results_df

    def save_event_results(self, file_path=''):

        file_name = f'Results_{self.official_name.replace(" ", "-")}.csv'

        if len(self.results_df) == 0:
            print(f'Results for "{self}" do not exist.')

        else:
            self.results_df.to_csv(file_path + file_name)
            print(f'{file_name} has been saved.')

        setattr(self, 'file_path', file_path)
        setattr(self, 'file_name', file_name)

        return None

    def event_namer(self):

        _name = self.official_name \
            .replace('DGPT', '') \
            .replace('PDGA', '') \
            .replace('Elite', '') \
            .replace('ET#6', '') \
            .replace('-', '') \
            .replace('+', '') \
            .upper().strip()

        if 'PRESENT' in _name:
            if 'PRESENTED' in _name:
                event_name = _name.split('PRESENTED')[0].strip()
            elif 'PRESENTS' in _name:
                event_name = _name.split('PRESENTS')[-1].strip()

        elif 'POWERED' in _name:
            event_name = _name.split('POWERED')[0].strip()

        else:
            event_name = _name.strip()

        event_name = event_name.replace(str(self.year), '').replace('PLAY IT AGAIN SPORTS', '').replace('  ',
                                                                                                        ' ').strip()

        return f"{event_name}, {self.year}"


class Player(PlayerSearch):

    def __init__(self, search_name=None, url=None, is_active=False, year=dt.today().year):

        if search_name:
            self._search_name = search_name.strip().title()
            self._search_first_name = self._search_name.split(' ')[0]
            self._search_last_name = self._search_name.split(' ')[-1]

        if not url:
            self._base_url = 'https://www.pdga.com/players'
            self.search_url = f'{self._base_url}?FirstName={self._search_first_name}&LastName={self._search_last_name}'

            _soup = soupify(self.search_url)

            self.pdga_number = int(_soup.select('td[class*="pdga-number"]')[0].text.strip())

            self.url = f'https://www.pdga.com/player/{self.pdga_number}'

        else:
            self._base_url = None
            self.search_url = None
            self._search_first_name = None
            self._search_last_name = None
            self.url = url
            self.pdga_number = int(self.url.split('/')[-1])

        _soup = soupify(self.url)

        try:
            _name_raw = soup.select('div[class*="pane-page-title"]')[0].text.strip()
        except:
            _name_raw = re.findall('<h1>(.+) #\d{1,7}<\/h1>', str(_soup))[0]
        self.official_name = _name_raw.split('#')[0].strip()
        self.first_name = self.official_name.split(' ')[0]
        self.last_name = self.official_name.split(' ')[-1]
        rating_raw = _soup.select('li[class*="rating"]')[0].text.strip()
        self.rating = int(re.findall(' (\d{3,4}) ', rating_raw)[0])

        self.player_results = {}
        self.player_stats = {
            'total_score': {},
            'number_of_events': {},
            'average_score': {},
            'best_score': {},
            'worst_score': {},
            'median_score': {},
        }

        self.is_active = is_active

    def __repr__(self):
        return self.official_name

    def __eq__(self, val):
        return self.official_name == val

    def fantasy_score(self, event, verbose=0):

        player = self.official_name
        results = event.results_df
        year = event.year
        event_name = event.table_name

        max_score = max([x for x in results.Place.values if str(x).isnumeric()])

        if player in results.Player.values:

            score = results[results.Player == player].Place.values[0]

            if score == 'DNF':
                score = max_score + 1
                # in_event = 1

            elif score == 'ERROR':
                if verbose:
                    print(f'Something went wrong for {player} in the "{event}" event.')
                # in_event = 0

                pass

            # else:
            #     in_event = 1

            self.player_results[year][event_name] = score

            # if event_name in self.player_results.keys():
            #     self.total_score -= self.player_results[event_name]

            # else:
            #     self.number_of_events += in_event

            # self.total_score += int(score)

            self.player_stats['total_score'][year] = sum(self.player_results[year].values())
            self.player_stats['number_of_events'][year] = len(self.player_results[year])

            if self.player_stats['number_of_events'][year]:
                self.player_stats['average_score'][year] = round(
                    self.player_stats['total_score'][year] / self.player_stats['number_of_events'][year], 3)

            return score

        else:
            if verbose:
                print(f'{player} did not play in the {event}.')
            pass

    def years_results(self, year, i=0):

        player = self.official_name

        results = self.player_results[year]
        total_score = sum(results.values())
        number_of_events = len(results)
        if number_of_events:
            self.player_stats['average_score'][year] = round(total_score / number_of_events, 3)
            self.player_stats['best_score'][year] = min(results.values())
            self.player_stats['worst_score'][year] = max(results.values())
            self.player_stats['median_score'][year] = median(results.values())
        else:
            self.player_stats['average_score'][year] = 0
            self.player_stats['best_score'][year] = 0
            self.player_stats['worst_score'][year] = 0
            self.player_stats['median_score'][year] = 0

        if i:
            player_line = f'{i}. {player}'
        else:
            player_line = f'-- {player} --'

        separator = '*' * (len(player_line) + 2)

        return f"""{separator}
 {player_line}
{separator}
Number of events: {self.player_stats['number_of_events'][year]}
Total score: {self.player_stats['total_score'][year]}
Average score: {self.player_stats['average_score'][year]:.3f}
Best score: {self.player_stats['best_score'][year]}
Worst score: {self.player_stats['worst_score'][year]}
Median score: {self.player_stats['median_score'][year]:.3f}
"""

    # Weighted average: {round(self.total_score / (self.number_of_events * 0.5), 3):.3f}

    def update_status(self, activate=True):

        action_dict = {
            True: 'active',
            False: 'inactive'
        }

        if self.is_active == activate:
            print(f'{player} is already {action_dict[activate]}')
        else:
            player.is_active = activate

        return None


class League:
    def __init__(
            self,
            name=None,
            teams=[],
            players=[],
            team_total_limit=9,
            team_active_limit=5,
            year=dt.today().year,
            player_table_name='Players',
            league_table_name='League'
    ):

        self.name = name.strip()
        self.teams = teams
        self.players = players
        self.team_names = [team.name for team in self.teams]
        self.team_owners = [team.owner for team in self.teams]
        self.team_rosters = [team.roster for team in self.teams]
        self._team_total_limit = team_total_limit
        self._team_active_limit = team_active_limit
        self.player_table_name = player_table_name
        self.league_table_name = self.name if name else league_table_name
        self.player_data = self.create_player_data()

        self.player_table_exists_query = table_exists(self.player_table_name)

        self.player_create_table_query = create_table(self.player_table_name, player_table_dict())

        self.player_insert_values_query = insert_data(
            self.player_table_name,
            player_table_dict(),
            self.player_data
        )

        self.league_table_exists_query = table_exists(self.league_table_name)

        self.league_create_table_query = create_table(self.league_table_name, league_table_dict())

        self.build_league_table()

    def __repr__(self):
        return self.name

    def create_player_data(self):
        players_for_postgres = []

        for player in self.players:
            for year, results in player.player_results.items():
                for event_name, place in results.items():
                    _dict = {
                        'Name': player.official_name,
                        'PDGA Number': player.pdga_number,
                        'Event Name': event_name,
                        'Place': place,
                        'Event Year': year,
                        'Event Status': 'Complete'
                    }

                    players_for_postgres.append(_dict)

        return players_for_postgres

    def build_player_table(self):

        connection, postgres = connect_to_sql()

        postgres.execute(self.player_table_exists_query)

        if not postgres.fetchone():
            print(f'Table named "{self.player_table_name}" does not exist.')
            postgres.execute(self.player_create_table_query)

        else:
            print(f'Table named "{self.player_table_name}" already exists.')
            pass

        postgres.execute(self.player_insert_values_query)

        print(f'Values inserted into "{self.player_table_name}" table.')

        close_connection(connection, postgres)

        return None

    def build_league_table(self):

        connection, postgres = connect_to_sql()

        postgres.execute(self.league_table_exists_query)

        if not postgres.fetchone():
            postgres.execute(self.league_create_table_query)
            print(f'Table named "{self.league_table_name}" has been created.')

        else:
            print(f'Table named "{self.league_table_name}" already exists.')
            pass

        close_connection(connection, postgres)

        return None


class Team:

    def __init__(
            self,
            owner,
            name,
            available_players,
            roster=[],
            league_table_name='League'

    ):

        self.owner = owner.strip().title()
        self.name = name.strip().title()
        self._active_limit = 5
        self.roster = roster
        self.player_count = len(self.roster)
        self.league = None,
        self.league_table_name = league_table_name

        self.insert_initial_data()

    def __repr__(self):
        return f'{self.name}, owned by {self.owner}'

    def __iadd__(self, player):

        if type(player) in [Player, str]:

            if player in available_players:

                if player not in self.roster:

                    if len(self.roster) < self._limit:

                        self.roster += [player]
                        _message = f'{player} has been added to {self.name}'

                        if self.player_count <= self._active_limit:
                            player.is_active = True
                            _message += ' and set to active'

                        else:
                            player.is_active = False

                    else:
                        _message = f'{self.name} must drop a player before adding another'

                else:
                    _message = print(f'{player} is already a member of {self.name}')

            else:
                _message = print(f'{player} is not available')

            print(_message + '.')

            return self

        else:
            raise TypeError(f"must be Player or str, not {_type}")

    def __isub__(self, player):

        _type = type(player)

        if _type in [Player, str]:

            if player in self.roster:

                _index = self.roster.index(player)

                self.roster[_index].is_active = False

                del self.roster[_index]

                print(f'{player} has been dropped from {self.name}')

            else:
                print(f'{player} is not a member of {self.name}')

            return self

        else:
            raise TypeError(f"must be Player or str, not {_type}")

    @property
    def roster(self):
        return self._roster

    @roster.setter
    def roster(self, val):
        self._roster = val
        self.player_count = len(self._roster)
        self.active_roster = [player for player in self._roster if player.is_active]
        self.active_player_count = len(self.active_roster)
        self.active_spots_remaining = self._active_limit - self.active_player_count

    def count_active_players(self):

        _number_of_active_players = len(self.active_roster)

        return _number_of_active_players

    def count_active_players(self):

        _number_of_active_players = len([player for player in self.roster if player.is_active])

        return _number_of_active_players

    def update_player(self, player, action):

        if player not in self.roster:
            print(f'{player} is not a member of {self.name}')
            return None

        action_dict = {
            'activate': True,
            'deactivate': False
        }

        player.update_status(action_dict[action])
        # self.number_of_active_players = self.count_active_players()

        return None

    def team_results(self, active_only=False):

        _total_score = 0
        _number_of_events = 0

        if self.roster:
            if active_only:
                _roster = self.active_roster

            else:
                _roster = self.roster

            for player in _roster:
                _total_score += player.player_stats['total_score'][year]
                _number_of_events += player.player_stats['number_of_events'][year]

            if _number_of_events:
                _average_score = _total_score / _number_of_events

                _message = f"""Number of events: {_number_of_events}
Total score: {_total_score}
Average score: {_average_score:.3f}
"""
            # Weighted average: {round(_total_score / (_number_of_events * 0.5), 3):.3f}

            else:
                _message = f'The players on {self.name} have not played in any events.'

        else:
            _message = f'{self.name} has no players.'

        print(_message)

        return None

    def insert_initial_data(self):

        connection, postgres = connect_to_sql()

        data = [{
            'Team Name': self.name,
            'Team Owner': self.owner,
            'Number of Players': 0,
            'Number of Active Players': 0,
            'Wins': 0,
            'Losses': 0,
            'Ties': 0,
            'First Place': 0,
            'Second Place': 0,
            'Third Place': 0,
        }]

        query = insert_data(self.league_table_name, league_table_dict(), data, truncate=False)

        postgres.execute(f'''SELECT 1
FROM "{self.league_table_name}"
WHERE "Team Name"='{self.name}'
''')

        if not postgres.fetchone():
            postgres.execute(query)
            print(f'"{self.name} inserted into "{self.league_table_name}".')

        else:
            print(f'"{self.name} already exists in "{self.league_table_name}".')
            pass

        close_connection(connection, postgres)

        return None


# print(Player(url="https://www.pdga.com/player/75412").__dict__)