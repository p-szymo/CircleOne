# app building library
import streamlit as st
from live_scrape import score_it # live_scorer, current_player_score
from teams import teams

# title
st.title('CIRCLE ONE')
st.header('INNOVA OUR HEADS')

league = teams()
event_number = 77763
wait_time = 2

# @st.cache_data
# def score_it(league, event_number, wait_time=5, to_print=False):

# format blank space
st.markdown('')

if st.button('Show me the scores!'):

    # format blank space
    st.markdown('')
    data_load_state = st.text('Loading data...')

    # generate live scores
    league_totals, team_scores_by_player = score_it(league, event_number, wait_time)

    data_load_state.text("Done!")

    # format blank space
    st.markdown('')
    st.markdown('# LEAGUE TOTALS')
    st.text(league_totals)

    # format blank space
    st.markdown('')
    st.markdown('# PLAYER TOTALS')
    st.text(team_scores_by_player)