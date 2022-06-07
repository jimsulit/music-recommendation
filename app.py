import streamlit as st
st.set_page_config(page_title="Song Recommendation", layout="wide")

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components

@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("filtered_track_df3_final.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

genre_names = ['acoustic opm', 'classic opm', 'deep neofolk', 'opm', 'pinoy alternative rap', 'pinoy hip hop', 'pinoy indie',
                'pinoy metal', 'pinoy pop punk', 'pinoy praise', 'pinoy r&b', 'pinoy reggae', 'pinoy rock'   
               ] # removed 'manila sound' and 'pinoy idol pop' 
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo", "mood_label"]

exploded_track_df = load_data()

def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    print("it passed here")
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity_x', ascending=False)[:50]

    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())

    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
    print("it passed here #2")
    uris = genre_data.iloc[n_neighbors]["track_id"].tolist() #change "" value to track_id from uri
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios


title = "Original Pilipino Music (OPM) Recommendation Engine"
st.title(title)

st.write("Try playing around with the different settings and listen to the songs recommended by the system according to your preference. 😃")
st.write("Created with ♥️ and ☕️ by Jimson Sulit as a requirement for IS 295B.")
st.markdown("##")

with st.container():
    col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
    with col3:
        st.markdown("***Filter recommendation by genre:***")
        genre = st.radio(
            "",
            genre_names, index=genre_names.index("opm"))
    with col1:
        st.markdown("***Choose your music recommendation preference:***")
        # start_year, end_year = st.slider(
        #     'Select the year range',
        #     1980, 2019, (2015, 2019)
        # )
        acousticness = st.slider(
            'Do you want your music to contain a variety of instruments? Slide left for a variety of instruments, slide right for less instruments in your recommendations.',
            0.0, 1.0, 0.5)
        danceability = st.slider(
            'Do you want your music mellow OR danceable? Slide left for more mellow, slide right for more danceable recommendations.',
            0.0, 1.0, 0.5)
        energy = st.slider(
            'Do you want your music quiet OR loud? Slide left for more quiet, slide right for more loud recommendations.',
            0.0, 1.0, 0.5)
        instrumentalness = st.slider(
            'Do you want more vocals OR more music? Slide left for more vocals, slide right for more instrumental recommendations.',
            0.0, 1.0, 0.0)
        valence = st.slider(
            'Do you want your music theme to be negative or positive? Slide left for more negative, slide right for more positive recommendations',
            0.0, 1.0, 0.45)
        tempo = st.slider(
            'Do you want your music to be slow or fast? Slide left for more slow music, slide right for more upbeat music recommendations',
            0.0, 244.0, 118.0)
        mood_label = st.slider(
            'Do you want your music to be sadder or happier? Slide left for more sad music, slide right for happier music recommendations',
            1.0, 4.0, 1.0)
start_year = 1980
end_year = 2018 
tracks_per_page = 6
test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo, mood_label]
uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)

tracks = []
for uri in uris:
    track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
    tracks.append(track)

if 'previous_inputs' not in st.session_state:
    st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat

current_inputs = [genre, start_year, end_year] + test_feat
if current_inputs != st.session_state['previous_inputs']:
    if 'start_track_i' in st.session_state:
        st.session_state['start_track_i'] = 0
    st.session_state['previous_inputs'] = current_inputs

if 'start_track_i' not in st.session_state:
    st.session_state['start_track_i'] = 0

with st.container():
    col1, col2, col3 = st.columns([2,1,2])
    if st.button("Recommend More Songs"):
        if st.session_state['start_track_i'] < len(tracks):
            st.session_state['start_track_i'] += tracks_per_page

    current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    if st.session_state['start_track_i'] < len(tracks):
        for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
            if i%2==0:
                with col1:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("See more details"):
                        df = pd.DataFrame(dict(
                        r=audio[:5],
                        theta=audio_feats[:5]))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=400, width=340)
                        st.plotly_chart(fig)
        
            else:
                with col3:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("See more details"):
                        df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_feats[:5]))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=400, width=340)
                        st.plotly_chart(fig)

    else:
        st.write("No songs left to recommend")