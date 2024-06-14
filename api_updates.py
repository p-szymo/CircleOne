import requests
import json
import pandas as pd
from datetime import datetime
from general_functions import second_tuesdays, to_datetime
from league import update_player_rating, event_parser
import urllib.parse as ulp


def retrieve_table(domain, table_name, headers, page_size=100):

    offset = 0
    table = []

    # COUNT OBJECT
    url = f'https://{domain}/api/data/{table_name}/count'
    r = requests.get(url=url, headers=headers)
    row_count = int(r.json())
    while offset < row_count:
        url = f'https://{domain}/api/data/{table_name}?pageSize={page_size}&offset={offset}'
        r = requests.get(url=url, headers=headers)
        table += r.json()
        offset += page_size

    return pd.DataFrame(table)


def player_rating_needs_update(date):
    if not date:
        return True

    else:
        # default value
        prev_update_day = None
        right_now = datetime.now()
        update_days = second_tuesdays()
        for i, day in enumerate(update_days):
            if right_now < day:
                # next_update_day = day
                prev_update_day = update_days[i - 1]
                break

        return date < prev_update_day


def update_player_ratings(domain, table_name, headers):
    num_players_updated = 0

    df = retrieve_table(domain=domain, table_name=table_name, headers=headers).fillna(0)

    for i, row in df.iterrows():
        pdga_number = row['PlayerID']
        row_id = row['objectId']
        last_updated = row['PlayerRatingLastUpdated']

        if player_rating_needs_update(to_datetime(last_updated)):
            updated_rating = update_player_rating(pdga_number)
            updated_at = datetime.now()
            json_data = {
                'PlayerRating': updated_rating,
                'PlayerRatingLastUpdated': updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            r = requests.put(
                f'https://{domain}/api/data/{table_name}/{row_id}',
                headers=headers,
                json=json_data,
            )
            num_players_updated += 1

    print(f'Number of player ratings updated: {num_players_updated}')

    return None


# def create_url(table_name, where)


def object_exists(domain, table_name, headers, where=''):

    url = f'https://{domain}/api/data/{table_name}/count'

    if where:
        url_where = ulp.quote(where)
        url += '?where=' + url_where
        print(url)

    r = requests.get(url=url, headers=headers)
    row_count = int(r.json())

    return bool(row_count)


    # event_in_table = object_exists(domain=domain, table_name=table_name, headers=headers, where=f'EventID={event}')
def add_event(domain, headers, event_records, table_name='EventResults'):

    print(f'https://{domain}/api/data/bulkupsert/{table_name}/')

    r = requests.put(
        f'https://{domain}/api/data/bulkupsert/{table_name}/',
        headers=headers,
        json=event_records,
    )

    return r.json()


def update_event(domain, headers, event_records, table_name='EventResults'):

    # r = requests.put(
    #     f'https://{domain}/api/data/bulkupsert/{table_name}/',
    #     headers=headers,
    #     json=event_records,
    # )

    return 'Event already exists in table'


def add_or_update_event(domain, headers, event_number, table_name='EventResults'):

    event_exists = object_exists(domain=domain, table_name=table_name, headers=headers, where=f'EventID={event_number}')
    event_records = event_parser(event_number).to_dict('records')
    print(event_records[:5])
    for er in event_records:
        er['EventID'] = event_number

    if not event_exists:
        response = add_event(domain=domain, headers=headers, event_records=event_records, table_name=table_name)

    else:
        response = update_event(domain=domain, headers=headers, event_records=event_records, table_name=table_name)

    return response


    print(events[0].to_dict('records'))
