from general_scrape import events_list
from postgres import insert_event
from league import Player, Event
import pandas as pd
import time


def event_scraper(year, wait_time=1, to_print=False):
    event_details = events_list(year)
    event_details = [event for event in event_details if 'DOUBLES' not in event[0].upper()]

    events = []
    events_errors = []
    events_df = pd.DataFrame(columns=['EventID', 'PlayerID', 'Place', 'Score'])
    events_mapping_df = pd.DataFrame(columns=['EventID', 'EventName', 'Year'])

    for event_name, link in event_details:
        try:
            e = Event(name=event_name, url=link, year=year)
            events.append(e)
            events_df.append(e.results_df, ignore_index=True)
            events_mapping_df.append({
                'EventID': e.pdga_event_number,
                'EventName': e.official_name,
                'Year': year
            })
        except:
            if to_print: print('ERROR: link')
            events_errors.append(link)
        time.sleep(wait_time)

    return events, events_errors, events_df, events_mapping_df


def player_scraper(pdga_number, wait_time=1, to_print=False):

    link = f'https://www.pdga.com/player/{pdga_number}'
    try:
        player = Player(url=link)
    except:
        if to_print: print(link)
        player = {
            'pdga_number': pdga_number,
            'url': link,
            'official_name': '',
            'first_name': '',
            'last_name': '',
            'rating': 0,
            'is_active': False
        }

    time.sleep(wait_time)

    return player

    print('Number of players:', len(players))
    print('Number of errors:', len(player_errors))

########################
# SCRAPE/INSERT EVENTS #
########################

all_events_df = pd.DataFrame(columns=['EventID', 'PlayerID', 'Place', 'Score'])
all_events_mapping_df = pd.DataFrame(columns=['EventID', 'EventName', 'Year'])

years_to_pull = [2023, 2024]

all_events = []
for year in years_to_pull:
    events, events_errors, events_df, events_mapping_df = event_scraper(year, wait_time=0.5, to_print=False)
    print(f'''{year} events: {len(events)} | {year} errors: {len(events_errors)} ''')

    all_events_df.append(events_df, ignore_index=True)
    all_events_mapping_df.append(events_mapping_df, ignore_index=True)

    # for event in events:
    #     all_events.append(event)
    #     file_name = event.official_name.replace(str(year), '').strip() + '.csv'
    #     event.results_df.to_csv(f'data/{file_name}', index=False)
    #     insert_event(event, to_print=True)

all_events_df.to_csv('data/EventResults.csv', index=False)
all_events_mapping_df.to_csv('data/Events.csv', index=False)


#########################
# SCRAPE/INSERT PLAYERS #
#########################

pdga_numbers_by_event = [event.results_df['PDGA Number'].values for event in all_events]

pdga_numbers = list(set([number for event in pdga_numbers_by_event for number in event]))

print(f'Number of players: {len(pdga_numbers)}')

players = []
player_errors = []

for number in pdga_numbers:
    link = f"https://www.pdga.com/player/{number}"
    try:
        players.append(Player(url=link))
    except:
        # print(link)
        players.append({
            'PlayerID': number,
            'PlayerName': None,
            'PlayerRating': 0,
            'PlayerURL': link,
            'IsActive': None,
            'IsOnTeam': None
        })
        player_errors.append(link)

    time.sleep(0.5)

print('Number of players:', len(players))
print('Number of errors:', len(player_errors))

all_players_data = []
for player in players:
    if type(player) == dict:
        all_players_data.append(player)

    else:
        all_players_data.append({
            'PlayerID': player.pdga_number,
            'PlayerName': player.official_name,
            'PlayerRating': player.rating,
            'PlayerURL': player.url,
            'IsActive': None,
            'IsOnTeam': None
        })

players_df = pd.DataFrame(all_players_data)
players_df.to_csv('data/Players.csv', index=False)