# app building library
import streamlit as st
from live_scrape import score_it # live_scorer, current_player_score
from teams import teams
from tour_schedule import event_status, schedule_2024

# title
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image('img/shitty_logo.png', width=75)
with col2:
    st.title('CIRCLE ONE')

st.header('INNOVA OUR HEADS')

league = teams()
wait_time = 2

# format blank space
st.markdown('')

event_number, status = event_status(schedule_2024())

st.markdown('## ' + status)
st.markdown('')

if status.split(' ')[0] == 'CURRENT':
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