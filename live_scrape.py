from bs4 import BeautifulSoup as bs
from teams import teams
import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


def live_scorer(event_id, wait_time=5):
    event_results = {}
    url = f'https://www.pdga.com/apps/tournament/live/event?view=Scores&eventId={event_id}&division=MPO'

    @st.cache_resource
    def get_driver():
        return webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")

    driver = get_driver()

    driver.get(url)
    time.sleep(wait_time)

    html = driver.page_source
    soup = bs(html, 'html.parser')
    rows = soup.select('div[class="table-row"]')

    for i, row in enumerate(rows):
        player_first_name = row.select_one('span[class="player-first-name"]').text
        player_last_name = row.select_one('span[class="player-last-name"]').text
        player_name = player_first_name + ' ' + player_last_name
        player_place_raw = row.select_one('span[class*="py-2"]').text

        if player_place_raw:
            if player_place_raw[0] == 'T':
                player_place = int(player_place_raw[1:])
            else:
                player_place = int(player_place_raw)

            par = row.select_one('div[class="label-1-semibold"]')

            if par:
                dnf = par.text.upper() == 'DNF'
            else:
                dnf = False

        else:
            player_place = 0
            dnf = False

        event_results[player_name] = {'place': player_place, 'dnf': dnf}

    event_results['Josh'] = {'place': 1, 'dnf': False}

    return event_results


def current_player_score(results, player):
    not_playing = False
    dnf = False
    max_score = max([v['place'] for v in results.values()])

    if player in results.keys():
        player_score = results[player]['place']
        if results[player]['dnf']:
            dnf = True

    else:
        player_score = max_score
        not_playing = True

    return player_score, not_playing, dnf


def current_team_score(results, team):
    not_playing = []
    dnf = []
    flagged = []
    max_score = max([v['place'] for v in results.values()])

    starters = team['starters']
    bench = team['bench']

    team_results = {}
    bench_results = {}

    for player in starters:
        player_score, not_playing_flag, dnf_flag = current_player_score(results, player)
        if not_playing_flag or dnf_flag:
            flagged.append(player)
            if not_playing_flag:
                not_playing.append(player)
            else:
                dnf.append(player)

        else:
            team_results[player] = player_score

    if flagged:
        for player in bench:
            player_score, not_playing_flag, dnf_flag = current_player_score(results, player)
            bench_results[player] = player_score

        sorted_bench = [(k, v) for k, v in sorted(bench_results.items(), key=lambda item: item[1])]

        for i, flagged_player in enumerate(flagged):
            potential_player = sorted_bench[i][0]
            potential_player_score = sorted_bench[i][1]
            if potential_player_score < max_score:
                team_results[potential_player] = potential_player_score
                if current_player_score(results, potential_player)[2]:
                    dnf.append(potential_player)
            else:
                team_results[flagged_player] = max_score

    total_score = sum(sorted(team_results.values())[:5])
    return total_score, not_playing, dnf, team_results

def score_it(league, event_number, wait_time=5, to_print=False):

    prologue = ''
    results = live_scorer(event_number, wait_time=wait_time)
    places = [v['place'] for k,v in results.items()]

    if not sum(places):
        league_print_string = 'There are no results yet.'
        teams_print_string = ''

    else:
        # at least one player doesn't have a place value
        if not min(places):
            prologue = '***** NOTE: Results may be incomplete... *****\n\n'

        scores = {}
        team_results = {}

        for team in league:
            owner = team['owner']

            score, not_playing, dnf, team_result = current_team_score(results, team)

            if not_playing:
                addenda = ' # not playing: ' + ' | '.join(not_playing)
            else:
                addenda = ''

            if dnf:
                addenda += ' # did not finish: ' + ' | '.join(dnf)

            scores[owner] = {'score': score, 'addenda': addenda}
            team_results[owner] = team_result

        sorted_scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1]['score'])}

        printout = []

        for owner, score in sorted_scores.items():
            line = f"{owner}: {str(score['score'])}{score['addenda']}"
            printout.append(line)

        league_print_string = prologue + '\n'.join(printout)
        if to_print: print(league_print_string + '\n')

        full_printout = []
        for owner, team_result in team_results.items():
            sorted_results = {k: v for k, v in sorted(team_result.items(), key=lambda item: item[1])}
            full_printout.append('\n' + owner)
            if to_print: print(owner)
            for player, score in sorted_results.items():
                player_score = f'{player}: {score}'
                full_printout.append(player_score)
                if to_print: print(player_score)

        teams_print_string = '\n'.join(full_printout)
        if to_print:
            print(teams_print_string)

    return league_print_string, teams_print_string


###########
# TESTING #
###########
# league = teams()
# event_number = 77764
#
# score_it(league, event_number, to_print=True)