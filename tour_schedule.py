from datetime import datetime, timedelta
import pytz

tz = pytz.timezone('US/Eastern')
right_now = datetime.now(tz)

def schedule_2024():
    return [
        {
            'EVENT_NAME': 'Chess.com Invitational',
            'EVENT_NUMBER': 77775,
            'START_DATE': '2024-02-23',
            'END_DATE': '2024-02-25'
        },
        {
            'EVENT_NAME': 'WACO',
            'EVENT_NUMBER': 77758,
            'START_DATE': '2024-03-07',
            'END_DATE': '2024-03-10'
        },
        {
            'EVENT_NAME': 'The Open at Austin',
            'EVENT_NUMBER': 77759,
            'START_DATE': '2024-03-15',
            'END_DATE': '2024-03-17'
        },
        {
            'EVENT_NAME': 'Texas State Disc Golf Championships',
            'EVENT_NUMBER': 77760,
            'START_DATE': '2024-03-20',
            'END_DATE': '2024-03-31'
        },
        {
            'EVENT_NAME': 'Jonesboro Open',
            'EVENT_NUMBER': 77761,
            'START_DATE': '2024-04-12',
            'END_DATE': '2024-04-14'
        },
        {
            'EVENT_NAME': 'Music City Open',
            'EVENT_NUMBER': 77762,
            'START_DATE': '2024-04-19',
            'END_DATE': '2024-04-21'
        },
        {
            'EVENT_NAME': 'PDGA Champions Cup',
            'EVENT_NUMBER': 77099,
            'START_DATE': '2024-04-25',
            'END_DATE': '2024-04-28'
        },
        {
            'EVENT_NAME': 'Dynamic Discs Open',
            'EVENT_NUMBER': 77763,
            'START_DATE': '2024-05-03',
            'END_DATE': '2024-05-05'
        },
        {
            'EVENT_NAME': 'OTB Open',
            'EVENT_NUMBER': 77764,
            'START_DATE': '2024-05-17',
            'END_DATE': '2024-05-19'
        },
        {
            'EVENT_NAME': 'Portland Open',
            'EVENT_NUMBER': 77765,
            'START_DATE': '2024-05-30',
            'END_DATE': '2024-06-02'
        },
        {
            'EVENT_NAME': 'Beaver State Fling',
            'EVENT_NUMBER': 77766,
            'START_DATE': '2024-06-07',
            'END_DATE': '2024-06-09'
        },
        {
            'EVENT_NAME': 'Preserve Championship',
            'EVENT_NUMBER': 78271,
            'START_DATE': '2024-06-21',
            'END_DATE': '2024-06-23'
        },
        {
            'EVENT_NAME': 'Des Moines Challenge',
            'EVENT_NUMBER': 77768,
            'START_DATE': '2024-07-05',
            'END_DATE': '2024-07-07'
        },
        {
            'EVENT_NAME': 'Ledgestone Open',
            'EVENT_NUMBER': 77769,
            'START_DATE': '2024-08-01',
            'END_DATE': '2024-08-04'
        },
        {
            'EVENT_NAME': 'LWS Open at Idlewild',
            'EVENT_NUMBER': 77771,
            'START_DATE': '2024-08-09',
            'END_DATE': '2024-08-11'
        },
        {
            'EVENT_NAME': 'Professional Disc Golf World Championships',
            'EVENT_NUMBER': 71315,
            'START_DATE': '2024-08-21',
            'END_DATE': '2024-08-25'
        },
        {
            'EVENT_NAME': 'Great Lakes Open',
            'EVENT_NUMBER': 77772,
            'START_DATE': '2024-09-05',
            'END_DATE': '2024-09-08'
        },
        {
            'EVENT_NAME': 'MVP Open',
            'EVENT_NUMBER': 77773,
            'START_DATE': '2024-09-26',
            'END_DATE': '2024-09-29'
        },
    ]

tour = schedule_2024()

def is_live(event):

    start_date = event['START_DATE']
    end_date = event['END_DATE']
    start_live_results = tz.localize(
        datetime.strptime(start_date, "%Y-%m-%d") + timedelta(hours=12),
        is_dst=None
    )
    end_live_results = tz.localize(
        datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=3, hours=12),
        is_dst=None
    )

    return start_live_results <= right_now <= end_live_results



def is_future_event(event):

    start_date = event['START_DATE']
    start_live_results = tz.localize(
        datetime.strptime(start_date, "%Y-%m-%d") + timedelta(hours=12),
        is_dst=None
    )

    return right_now <= start_live_results


def event_status(schedule):

    next_event = {
        'EVENT_NUMBER': 0,
        'EVENT_NAME': 'n/a'
    }
    next_event_number = -1

    for i, event in enumerate(schedule):
        if is_live(event):
            return event['EVENT_NUMBER'], f"CURRENT EVENT - TOUR STOP #{i+1} - {event['EVENT_NAME']}"

    for i, event in enumerate(reversed(schedule)):
        if is_future_event(event):
            next_event = event
            next_event_number = len(schedule) - i
        else:
            datestring = datetime.strptime(event['START_DATE'], "%Y-%m-%d").strftime("%B %-d")
            message = f"""NEXT EVENT - TOUR STOP #{next_event_number} - {next_event['EVENT_NAME']}
### Check back on {datestring} at noon"""
            return next_event['EVENT_NUMBER'], message


print(event_status(tour))






    # tour_number = i+1
    # event_name = event['EVENT_NAME']
    # event_number = event['EVENT_NUMBER']
    # start_date = event['START_DATE']
    # end_date = event['END_DATE']
    # start_live_results = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(hours=12)
    # end_live_results = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=3, hours=12)
    # start_string = start_live_results.strftime("%Y-%m-%d %I:%M%p")
    # end_string = end_live_results.strftime("%Y-%m-%d %I:%M%p")
    #
    # print(f'Tour stop #{tour_number}: {event_name}')
    # print(f'Start date: {start_date}')
    # print(f'End date: {end_date}')
    # print(f'Results available between: {start_string} and {end_string}')
    # print()