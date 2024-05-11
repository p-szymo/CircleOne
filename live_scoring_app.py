# app building library
import streamlit as st
from live_scrape import score_it
from teams import teams

# title
st.title('CIRCLE ONE')
st.header('INNOVA OUR HEADS')

league = teams()
event_number = 77763
wait_time = 2

# format blank space
st.markdown('')
# format blank space
st.markdown('')

if st.button('Show me the scores!'):

    # generate live scores
    league_totals, team_scores_by_player = score_it(league, event_number, wait_time)

    # format blank space
    st.markdown('')
    st.markdown('# LEAGUE TOTALS')
    st.text(league_totals)

    # format blank space
    st.markdown('')
    st.markdown('# PLAYER TOTALS')
    st.text(team_scores_by_player)