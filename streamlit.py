import streamlit as st
import pandas as pd
import folium
import pickle
from google_images_search import GoogleImagesSearch
import utils_streamlit as ut
import json


if 'users' not in st.session_state:
    st.session_state['users'] = []
if 'page' not in st.session_state:
    st.session_state['page'] = 1
if 'search_keys' not in st.session_state:
    st.session_state['search_keys'] = pickle.load(open("Search_engine_keys.pickle","rb"))
if 'search' not in st.session_state:
    st.session_state['search'] = GoogleImagesSearch(st.session_state['search_keys']["api"],st.session_state['search_keys']["cx"])
if 'data' not in st.session_state:
    st.session_state['data'] = json.load(open('./Data/data.json'))
if 'location' not in st.session_state:
    st.session_state['location'] = (41.3808593, 2.1746778)

if st.session_state['page'] == 1:
############## PAGE 1 ###############
    st.markdown("<h1 style='text-align: center; color: white;'>Tell us who is coming 🍽️</h1>", unsafe_allow_html=True)

    user = st.text_input("Username")
    add = st.button("Add", key=1)

    st.header("Attendance list")

    if add:
        st.session_state['users'].append(user)

    col1, mid, col2 = st.columns([1,1,20])
    for usr in st.session_state['users']:
        with col1:
            st.image("./demo_images/"+usr+".png", width=50)
        with col2:
            st.subheader(usr)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        next = st.button("Find restaurants!",key = 2)

    if next:
        st.session_state["page"] = 2
        st.experimental_rerun()

############## PAGE 2 ###############
elif st.session_state['page'] == 2:
    st.markdown("<h1 style='text-align: center; color: white;'>We think you would like:</h1>", unsafe_allow_html=True)

    # SIDEBAR
    st.sidebar.title("Filters")
    filter_distance = st.sidebar.slider(
        "Distance (m)", 0, 2000
    )
    filter_price = st.sidebar.select_slider(
        "Price",
        options=["€", "€€", "€€€", "€€€€"]
    )

    r_data = [ut.get_restaurant_data(st.session_state["data"], i) for i in range(5)]
    # mapa foto nombre
    m = folium.Map(location=list(st.session_state["location"]), zoom_start=13)

    for rest in r_data:
        folium.Marker(
            list(rest["coordinates"]), popup=folium.Popup("<b>"+str(rest["rating"])+"/5</b> \n"+ "€"*rest["price"] +"\n 30m", max_width='100%'), tooltip=rest["name"]
        ).add_to(m)

    folium.CircleMarker(
        location=list(st.session_state["location"]),
        radius=10,
        popup="Your location",
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)

    m

    gps = [(41.3808593, 2.1746778),
        (41.3764155, 2.1497178),
        (41.398621999999996, 2.1753768),
        (41.376280099999995, 2.1902122),
        (41.386613, 2.1836629),
        (41.3843476, 2.1701418),
        (41.382691699999995, 2.1792861),
        (41.381510299999995, 2.1789191999999997),
        (41.3869009, 2.1611382999999997),
        (41.3868455, 2.1527996)]

    # SUGGESTIONS
    st.markdown("""---""")
    for rest in r_data:
        col1, space, col2, contact = st.columns([8,1,10,10])
        with col1:
            try:
                st.markdown("<img src=" +ut.find_image(st.session_state['search'],rest["name"]) + " width='200'/>", unsafe_allow_html=True)
            except:
                st.markdown("![Alt Text]("+rest['image']+")")
        with col2:
            st.subheader(rest["name"])
            st.write("⭐ "+str(rest["rating"]))
            st.write("€"*rest["price"])
            st.write("📍 42 m")

        with contact:
            st.header("")
            st.write("Phone: " + str(rest["phone"]))
            st.write("Website: " + str(rest["website"]))
            st.write("Address: " + str(rest["address"]))

        st.markdown("""---""")
