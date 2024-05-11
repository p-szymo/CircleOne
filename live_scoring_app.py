# app building library
import streamlit as st
from live_scrape import live_scorer, current_player_score
from teams import teams

# title
st.title('CIRCLE ONE')
st.header('INNOVA OUR HEADS')

league = teams()
event_number = 77763
wait_time = 2

@st.cache_data
def score_it(league, event_number, wait_time=5, to_print=False):
    results = live_scorer(event_number, wait_time=wait_time)
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

    league_print_string = '\n'.join(printout)
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
    if to_print: print(teams_print_string)

    return league_print_string, teams_print_string

# format blank space
st.markdown('')
data_load_state = st.text('Loading data...')
# format blank space
st.markdown('')

# generate live scores
league_totals, team_scores_by_player = score_it(league, event_number, wait_time)

data_load_state.text("Done! (using st.cache_data)")

if st.button('Show me the scores!'):

    # format blank space
    st.markdown('')
    st.markdown('# LEAGUE TOTALS')
    st.text(league_totals)

    # format blank space
    st.markdown('')
    st.markdown('# PLAYER TOTALS')
    st.text(team_scores_by_player)