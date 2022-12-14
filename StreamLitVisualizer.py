import streamlit as st
from BechdelTest import BechdelTest

bt = BechdelTest()

# set the title of the app
st.title('Movie Scripts Bechdel Test')

# get the list of available movies
data = bt.get_available_move_titles()

# create a column view for the select box and the button
with st.sidebar:
    col1, col2 = st.columns([7, 3])
    with col1:
        movieName = st.selectbox(options=data, label='Select a movie')
    with col2:
        st.text('')
        st.text('')
        clicked = st.button('Get Script')

    #details about levels of bechdel test
    st.text('Bechdel Score = 0:') 
    st.write('The script does not pass the Bechdel test.')
    st.text('Bechdel Score = 1:')
    st.write('This means that there is at least one named woman speaking in the movie.')
    st.text('Bechdel Score = 2:')
    st.write('1. There are at least one named woman speaking in the movie.')
    st.write('2. There are at least two women speaking to each other in the movie.')
    st.text('Bechdel Score = 3:')
    st.write('1. There are at least one named woman speaking in the movie.')
    st.write('2. There are at least two women speaking to each other in the movie.')
    st.write('3. The women where talking about something other than a man.')
        

# if the button is clicked, get the script and display it
if clicked:
    with st.spinner('Checking if the movie passes the Bechdel test...'):
        bechdelResult = bt.get_bechdel_score(movieName)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Our Bechdel Rating')
    with col2:
        st.subheader('Scraped Bechdel Rating')

    col = st.columns(9)
    with col[1]:
        st.header(str(bechdelResult) + "/3")
    with col[6]:
        # get the scraped bechdel score
        scrapedBechdelScore = 3
        st.header(str(scrapedBechdelScore) + "/3")

    # get the ratings of the movie
    ratingdf = bt.getMovieRating(movieName)    
    if len(ratingdf) > 0:
        # create a column view for the ratings with the number of ratings
        col = st.columns(3)
        with col[0]:
            st.subheader('IMDB')
            rating1 = ratingdf["Value"][0]
            st.header(rating1)
        with col[1]:
            st.subheader('Rotten Tomatoes')
            rating2 = ratingdf["Value"][1]
            # convert from % to fraction
            rating2 = str(int(rating2[:-1]) / 10) + "/10"
            st.header(rating2)
        with col[2]:
            st.subheader('Metacritic')
            rating3 = ratingdf["Value"][2]
            #convert from fraction of 100 to fraction of 10
            rating3 = str(int(rating3[:2]) / 10) + "/10"
            st.header(rating3)
    elif len(ratingdf)==0:
        st.subheader('No ratings found for this movie!')