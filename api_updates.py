import requests
import json
import pandas as pd
from datetime import datetime
from general_functions import second_tuesdays, to_datetime
from league import update_player_rating, event_parser
import urllib.parse as ulp


def retrieve_table(domain, table_name, headers, where='', page_size=100):

    if where:
        url_where = '?where=' + ulp.quote(where)
    else:
        url_where = ''

    offset = 0
    table = []

    # COUNT OBJECT
    url = f'https://{domain}/api/data/{table_name}/count{url_where}'
    r = requests.get(url=url, headers=headers)
    row_count = int(r.json())

    if url_where:
        url_where = url_where[1:] + '&'

    while offset < row_count:
        url = f'https://{domain}/api/data/{table_name}?{url_where}pageSize={page_size}&offset={offset}'
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


def batch_list(records):

    num_records = len(records)
    batches = [records[x:x+100] for x in range(0, num_records, 100)]
    num_batches = len(batches)
    if num_batches > 1:
        es = 'es'
    else:
        es = ''

    return batches, es


def add_event(domain, headers, event_records, table_name='EventResults'):

    num_records = len(event_records)
    event_batches, es = batch_list(event_records)
    num_batches = len(event_batches)

    for batch in event_batches:
        r = requests.put(
            f'https://{domain}/api/data/bulkupsert/{table_name}',
            headers=headers,
            json=batch,
        )

    return f'{num_records} records were inserted in {num_batches} batch{es}'


def update_event(domain, headers, event_records, event_number, table_name='EventResults'):

    updated_scores = {
        record['PlayerID']: {'place': record['Place'], 'score': record['Score']} for record in event_records
    }

    where = f'EventID={event_number}'

    df = retrieve_table(domain=domain, table_name=table_name, headers=headers, where=where).fillna(0)

    prev_scores = df.to_dict('records')

    for record in prev_scores:
        player = record['PlayerID']
        record['Place'] = updated_scores[player]['place']
        record['Score'] = updated_scores[player]['score']

    response = add_event(domain=domain, headers=headers, event_records=prev_scores, table_name=table_name)

    return response.replace('inserted', 'updated')


def add_or_update_event(domain, headers, event_number, table_name='EventResults'):

    event_exists = object_exists(domain=domain, table_name=table_name, headers=headers, where=f'EventID={event_number}')
    event_records = event_parser(event_number).to_dict('records')
    for er in event_records:
        er['EventID'] = event_number

    if not event_exists:
        response = add_event(domain=domain, headers=headers, event_records=event_records, table_name=table_name)

    else:
        response = update_event(
            domain=domain,
            headers=headers,
            event_records=event_records,
            event_number=event_number,
            table_name=table_name
        )

    return response
