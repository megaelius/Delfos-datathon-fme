import streamlit as st
import pandas as pd
import folium
import pickle
from google_images_search import GoogleImagesSearch
import Auxiliary.utils_streamlit as ut
import json
from Auxiliary.recommender import Recommender
import geocoder

if 'recommender' not in st.session_state:
    st.session_state["recommender"] = Recommender()
if 'users' not in st.session_state:
    st.session_state['users'] = []
if 'page' not in st.session_state:
    st.session_state['page'] = 1
if 'search_keys' not in st.session_state:
    st.session_state['search_keys'] = pickle.load(open("./Auxiliary/Search_engine_keys.pickle","rb"))
if 'search' not in st.session_state:
    st.session_state['search'] = GoogleImagesSearch(st.session_state['search_keys']["api"],st.session_state['search_keys']["cx"])
if 'data' not in st.session_state:
    st.session_state['data'] = json.load(open('./Data/data.json'))
if 'location' not in st.session_state:
    st.session_state['location'] = None
if 'customer_names' not in st.session_state:
    a = set()
    for restaurant in st.session_state['data']:
        for review in restaurant['reviews_data']:
            a.add(review['user']['name'])
    st.session_state['customer_names'] = list(a)
if 'max_price' not in st.session_state:
    st.session_state['max_price'] = 4
if 'max_dist' not in st.session_state:
    st.session_state['max_dist'] = 5

if st.session_state['page'] == 1:
############## PAGE 1 ###############
    st.markdown("<h1 style='text-align: center; color: white;'>Tell us who is coming 🍽️</h1>", unsafe_allow_html=True)

    user = st.selectbox('Find a user', st.session_state['customer_names'])
    # user = st.text_input("Username")
    add = st.button("Add", key=1)

    st.header("Attendance list")

    if add:
        st.session_state['users'].append(user)

    col1, mid, col2 = st.columns([1,1,20])
    for i,usr in enumerate(st.session_state['users']):
        with col1:
            if i < 5: st.image("./Demo_images/"+str(i)+".png", width=50)
            else: st.image("./Demo_images/default.png", width=50)
        with col2:
            st.subheader(usr)

    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        next = st.button("Find restaurants!",key = 2)

    if next:
        st.session_state["page"] = 2
        st.experimental_rerun()

############## PAGE 2 ###############
elif st.session_state['page'] == 2:


    # SIDEBAR
    st.sidebar.title("Filters")
    filter_distance = st.sidebar.select_slider(
        "Distance (km)", options=[0.25*i for i in range(1,21)], value=5
    )
    filter_price = st.sidebar.select_slider(
        "Price",
        options=["€", "€€", "€€€", "€€€€"],
        value = "€€€€"
    )

    st.session_state["max_dist"] = filter_distance
    st.session_state["max_price"] = len(filter_price)

    #Show results
    st.markdown("<h1 style='text-align: center; color: white;'>We think you would like:</h1>", unsafe_allow_html=True)
    recommended = st.session_state["recommender"].recommend_to_group(st.session_state["users"],5,coords_group = st.session_state["location"],max_price = st.session_state["max_price"], max_dist = st.session_state["max_dist"])
    r_data = [ut.get_restaurant_data(st.session_state["data"], i) for (_,i) in recommended]
    # mapa foto nombre
    if  st.session_state["location"] is None:
        m = folium.Map(location=list(ut.get_recommendations_centroid(r_data)), zoom_start=13)
    else:
        m = folium.Map(location=list(st.session_state["location"]), zoom_start=13)
    if not len(r_data):
        if st.session_state["location"] is not None:
            folium.CircleMarker(
                location=list(st.session_state["location"]),
                radius=10,
                popup="Your location",
                color="#3186cc",
                fill=True,
                fill_color="#3186cc",
            ).add_to(m)
        m
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            st.write("")
            locate = st.button("Locate Me", key=2)
        st.markdown("<h2 style='text-align: center; color: white;'>Ups! It looks like there aren't restaurants with this conditions.</h2>", unsafe_allow_html=True)
    else:
        for rest in r_data:
            if st.session_state["location"] is not None:
                folium.Marker(
                    list(rest["coordinates"]),
                    icon=folium.Icon(color="red", icon="info-sign"),
                    popup=folium.Popup("<b>"+str(rest["rating"])+"/5</b> \n"+ "€"*rest["price"] +"\n"+str(ut.compute_distances(st.session_state['location'],rest['coordinates']))+"m", max_width='100%'), tooltip=rest["name"]
                ).add_to(m)
            else:
                folium.Marker(
                    list(rest["coordinates"]),
                    icon=folium.Icon(color="red", icon="info-sign"),
                    popup=folium.Popup("<b>"+str(rest["rating"])+"/5</b> \n"+ "€"*rest["price"], max_width='100%'), tooltip=rest["name"]
                ).add_to(m)


        if st.session_state["location"] is not None:
            folium.CircleMarker(
                location=list(st.session_state["location"]),
                radius=10,
                popup="Your location",
                color="#3186cc",
                fill=True,
                fill_color="#3186cc",
            ).add_to(m)

        m

        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            st.write("")
            locate = st.button("Locate Me", key=2)

        if locate:
            st.session_state["location"] = geocoder.ip('me').latlng
            st.experimental_rerun()

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
                if st.session_state["location"] is not None:
                    st.write("📍"+str(ut.compute_distances(st.session_state['location'],rest['coordinates'])) + "m")

            with contact:
                st.header("")
                st.write("Phone: " + str(rest["phone"]))
                st.write("Website: " + str(rest["website"]))
                st.write("Address: " + str(rest["address"]))

            st.markdown("""---""")
