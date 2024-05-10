from general_functions import soupify, type_check
import itertools


def events_list(
    year,
    tier=['ES', 'M'],
    classification=['Pro'],
    base_url='https://www.pdga.com/tour/search',
):
    """
    Compile list of event links by year.


    Input
    -----
    year : int
        Year of event(s).

    tier : list => str
        Event tier code(s).
        Default : ['ES', 'M']

    classification : list => str
        Event classification name(s).
        Default : ['Pro']

    base_url : str
        URL prefix for event search.
        Default : 'https://www.pdga.com/tour/search'

    Output
    ------
    events_with_links : list => tuple => str
        Event names and URLs.
    """

    # convert tier list to url string
    tier_str = '&'.join([f'Tier[]={t}' for t in tier])
    # convert classification list to url string
    classification_str = '&'.join([f'Classification[]={c}' for c in classification])
    # build url
    url = f'{base_url}?date_filter[min][date]={year}-01-01&date_filter[max][date]={year}-12-31&{tier_str}&{classification_str}'

    # scrape url into beautifulsoup object
    soup = soupify(url)
    # generate list of event links
    events_with_links_raw = soup.select('a[href*="/tour/event/"]')
    # create list of event names and urls, if event name exists
    events_with_links = [
        (e.text, 'https://www.pdga.com' + e['href']) for e in events_with_links_raw if e.text
    ]

    return events_with_links


# DEPRECATED
# def players_links_list(
#     base_url='https://www.pdga.com/united-states-tour-ranking-open',
# ):
#     """
#     Compile list of player links (limited to base_url endpoint).
#
#     Input
#     -----
#     base_url : str
#         URL prefix for event search.
#         Default : 'https://www.pdga.com/tour/search'
#
#     Output
#     ------
#     players_links : list => tuple => str
#         Player URLs.
#     """
#
#     # scrape url into beautifulsoup object
#     soup = soupify(base_url)
#     # capture table object
#     table = soup.select_one('div[class*="table"]')
#     # generate list of player links
#     player_data = table.select('a[class*="player-profile-link"]')
#     # add url prefix to player links
#     players_links = [
#         ('https://www.pdga.com' + p['href']) for p in player_data if p.text.strip()
#     ]
#
#     return players_links


def player_links_list(events):
    """
    Compile list of player links based on events list.

    Input
    -----
    events : list => Event
        List of Event objects.

    Output
    ------
    players_links : list => str
        Player URLs (PDGA.com).
    """

    # compile list of player pdga numbers
    player_numbers = [event.results_df['PDGA Number'].values for event in events]

    # convert to unique list of full player urls
    player_links = list(
        set(
            # flatten list of player pdga numbers and add url prefix
            [f'https://www.pdga.com/player/{number}' for event in player_numbers for number in event]
        )
    )

    return player_links


class Search:

    def __init__(self, search_type, **kwargs):
        # standardize search type
        self._search_type = search_type.title()
        # instantiate search option base url and requirements
        self._search_options = {
            'Event': {
                'base_url': 'https://www.pdga.com/tour/search',
                'reqs': [
                    'event',
                    'date_filter_min',
                    'date_filter_max',
                    'tier',
                    'classification'
                ]
            },
            'Player': {
                'base_url': 'https://www.pdga.com/players',
                'reqs': [
                    'first_name',
                    'last_name'
                ]
            }
        }
        # specify potential url requirement names and data types
        self._search_dict = {
            'event': {'url': 'OfficialName', 'type': str},
            'date_filter_min': {'url': 'date_filter[min][date]', 'type': str},
            'date_filter_max': {'url': 'date_filter[max][date]', 'type': str},
            'tier': {'url': 'Tier[]', 'type': list},
            'classification': {'url': 'Classification[]', 'type': list},
            'first_name': {'url': 'FirstName', 'type': str},
            'last_name': {'url': 'LastName', 'type': str}
        }
        # instantiate necessary search elements
        self._base_url = self._search_options[self._search_type]['base_url']
        self._search_reqs = self._search_options[self._search_type]['reqs']
        # generate list of missing requirements
        _reqs_not_met = [x for x in self._search_reqs if x not in kwargs.keys()]
        # if at least one requirement is missing
        if _reqs_not_met:
            # grammatical formatting
            if len(_reqs_not_met) == 1:
                s = ''
                is_are = 'is'
            else:
                s = 's'
                is_are = 'are'
            # print message regarding missing requirements
            print(f"The following argument{s} {is_are} missing: {', '.join(reqs_not_met)}")

        # set keyword arguments as input
        self.input = kwargs
        # set search url prefix
        self.search_string = self._base_url + '?'
        # number of search requirements
        _number_of_reqs = len(self._search_reqs)
        # iterate through search requirements
        for i, item in enumerate(self._search_reqs):
            # capture input, url element, and data type of url element
            item_input = self.input[item]
            item_url_term = self._search_dict[item]['url']
            item_req_type = self._search_dict[item]['type']

            # confirm necessary data types for input elements
            type_check(item_input, item_req_type)

            # convert lists to &-separated strings
            if item_req_type == list:
                url_part = '&'.join([f'{item_url_term}={x}' for x in item_input])
            # build syntax for string elements
            elif item_req_type == str:
                url_part = f'{item_url_term}={item_input}'
            # catch-all error printout
            else:
                print('Something went wrong with _search_reqs')
            # replace spaces with url character
            self.search_string += url_part.replace(' ', '%20')
            # add `&` character between url elements but not at end of url
            if i != _number_of_reqs - 1:
                self.search_string += '&'

        # scrape url into beautifulsoup object
        self._soup = soupify(self.search_string)

    def parser_init(self):

        soup = self._soup
        table = soup.select('div[class*="table-container"]')[0]

        odd_rows = table.select('tr[class*="odd"]')
        even_rows = table.select('tr[class*="even"]')

        rows = [x for x in itertools.chain.from_iterable(itertools.zip_longest(odd_rows, even_rows)) if x]

        return rows


class EventSearch(Search):

    def __init__(self, **kwargs):
        Search.__init__(self, search_type='Event', **kwargs)

        self._event_details = self.parser()

        self.url = self._event_details[0]
        self.official_name = self._event_details[1]
        self.pdga_event_number = self._event_details[2]

    def parser(self, _base_url='https://www.pdga.com'):

        rows = self.parser_init()

        parsings = []
        for row in rows:
            if row.select('td[class*="views-field views-field-Classification"]')[0].text.strip() == 'Pro':
                event_link = row.select('a[href*="/tour/event/"]')[0]
                event_url = _base_url + event_link['href']
                event_official_name = event_link.text
                event_number = int(event_url.split('/')[-1])
                parsings.append((event_url, event_official_name, event_number))

        if len(parsings) > 1:
            print('There may be an issue as we parsed more than one item that matches.')

        event = parsings[0]

        return event[0], event[1], event[2]


class PlayerSearch(Search):

    def __init__(self, **kwargs):
        Search.__init__(self, search_type='Player', **kwargs)

        self._player_details = self.parser()

        self.url = self._player_details[0]
        self.official_name = self._player_details[1]
        self.pdga_number = self._player_details[2]

    def parser(self, _base_url='https://www.pdga.com'):

        rows = self.parser_init()

        parsings = []
        for row in rows:
            player_link = row.select('a[href*="player/"]')[0]
            player_url = _base_url + player_link['href']
            player_official_name = player_link.text
            player_number = int(player_url.split('/')[-1])
            parsings.append((player_url, player_official_name, player_number))

        if len(parsings) > 1:
            print('There may be an issue as we parsed more than one item that matches.')

        player = parsings[0]

        return player[0], player[1], player[2]


