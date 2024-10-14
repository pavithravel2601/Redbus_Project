import streamlit as st
import mysql.connector
import pandas as pd

# MySQL Connection
con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345678'
)
cursor = con.cursor()
cursor.execute("USE redbus_project")

# Load Data from SQL into DataFrame
df = pd.read_sql("SELECT * FROM Bus_route", con)

# Clean the 'Price' column: Remove non-numeric characters and convert to numeric
df['Price'] = df['Price'].replace('[\$,]', '', regex=True)  # Remove any commas or dollar signs if present
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')  # Convert to numeric, set non-convertibles to NaN

# Ensure 'Route_Link' is present in the DataFrame
if 'Route_Link' in df.columns:
    # Create HTML links in the DataFrame
    df['route_link'] = df['Route_Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
else:
    st.error("The 'Route_Link' column is missing in the database.")

# CSS Styling for Column Headers
st.markdown(
    """
    <style>
    .dataframe thead th {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    .dataframe tbody td {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Streamlit app
st.header('REDBUS DataScraping Project :bus:')

# Get the min and max price values from the DataFrame
min_price = int(df['Price'].min())
max_price = int(df['Price'].max())

# Initialize session state if not already set
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'state': 'All',
        'route': 'All',
        'bus': 'All',
        'bustype': 'All',
        'departure_time': 'All',
        'rating': 'All',
        'seat_avail': 'All',
        'price_range': (0, 5000) , # Set default price range
        'travel_date': pd.to_datetime('today').date(),
       # 'travel_time': pd.to_datetime('12:00').time()  # Default time set to noon
    }

# Define a form to hold the input elements and buttons
with st.form(key='filter_form'):
    # State Selection
    state_name = ['All'] + df['State'].drop_duplicates().tolist()
    statename = st.selectbox("Select your state:", state_name, key='state', index=state_name.index(st.session_state.form_values['state']))

    # Route Name Selection
    route_name = ['All'] + df['Route_Name'].drop_duplicates().tolist()
    routename = st.selectbox("Select your route:", route_name, key='route', index=route_name.index(st.session_state.form_values['route']))

    # Bus Name Selection
    bus_name = ['All'] + df['Bus_Name'].drop_duplicates().tolist()
    busname = st.selectbox("Select your bus:", bus_name, key='bus', index=bus_name.index(st.session_state.form_values['bus']))

    # Bus Type Selection
    bus_type = ['All'] + df['Bus_Type'].drop_duplicates().tolist()
    bustype = st.selectbox("Select your bus type:", bus_type, key='bustype', index=bus_type.index(st.session_state.form_values['bustype']))

    #Departure Time Checkboxes
    st.write("Select Departure Times:")
    before_6am_checkbox = st.checkbox("Before 6 AM")
    six_am_to_noon_checkbox = st.checkbox("6 AM to Noon")
    noon_to_six_pm_checkbox = st.checkbox("Noon to 6 PM")
    after_6pm_checkbox = st.checkbox("After 6 PM")

    # Travel Date Input (Date Picker)
    travel_date = st.date_input("Select your travel date:", value=st.session_state.form_values['travel_date'], key='travel_date')

    # Travel Time Input (Time Picker)
    #travel_time = st.time_input("Select your travel time:", value=st.session_state.form_values['travel_time'], key='travel_time')


    # Departing Time Selection
    unique_times = ["All"] + [f"{str(i).zfill(2)}:00" for i in range(24)]
    departure_time = st.selectbox("Select your departure time:", unique_times, key='departure_time', index=unique_times.index(st.session_state.form_values['departure_time']))

    # Star Rating Selection
   # rating = ['All', '*', '**', '***', '****', '*****']
   # star_rating = st.selectbox("Select your star rating:", rating, key='rating', index=rating.index(st.session_state.form_values['rating']))

    star_ratings = {
        'All': 'All',
        '*': '⭐',
        '**': '⭐⭐',
        '***': '⭐⭐⭐',
        '****': '⭐⭐⭐⭐',
    }
    star_rating = st.selectbox(
        "Select your star rating:",
        options=list(star_ratings.keys()),
        format_func=lambda x: star_ratings[x],  # Displays the stars
        key='rating',
        index=list(star_ratings.keys()).index(st.session_state.form_values['rating'])
    )

    # Seat Availability Selection
    seat_availability = ['All'] + df['Seat_Availability'].drop_duplicates().tolist()
    seat_avail = st.selectbox("Select your seat availability:", seat_availability, key='seat_avail', index=seat_availability.index(st.session_state.form_values['seat_avail']))

    # Price Range Slider
    price_range = st.slider(
        "Select your price range:",
        0, 5000,
        (0, 5000),  # Default range
        key='price_range'
    )

    # Create a Submit and Reset Button
    submit_button = st.form_submit_button(label='Submit')
    reset_button = st.form_submit_button(label='Reset')

# Handle the form submission
if submit_button:
    # Save the current values to session state
    st.session_state.form_values = {
        'state': statename,
        'route': routename,
        'bus': busname,
        'bustype': bustype,
        'departure_time': departure_time,
        'rating': star_rating,
        'seat_avail': seat_avail,
        'price_range': price_range, # Store price range as a tuple
        'travel_date': travel_date,
       # 'travel_time': travel_time
    }

    # Filter Data
    filtered_df = df.copy()

    if statename != 'All':
        filtered_df = filtered_df[filtered_df['State'] == statename]
    if routename != 'All':
        filtered_df = filtered_df[filtered_df['Route_Name'] == routename]
    if busname != 'All':
        filtered_df = filtered_df[filtered_df['Bus_Name'] == busname]
    if bustype != 'All':
        filtered_df = filtered_df[filtered_df['Bus_Type'] == bustype]

     # Time Filtering Logic
    if before_6am_checkbox:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Departing_Time']).dt.hour < 6]
    if six_am_to_noon_checkbox:
        filtered_df = filtered_df[(pd.to_datetime(filtered_df['Departing_Time']).dt.hour >= 6) & (pd.to_datetime(filtered_df['Departing_Time']).dt.hour < 12)]
    if noon_to_six_pm_checkbox:
        filtered_df = filtered_df[(pd.to_datetime(filtered_df['Departing_Time']).dt.hour >= 12) & (pd.to_datetime(filtered_df['Departing_Time']).dt.hour < 18)]
    if after_6pm_checkbox:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Departing_Time']).dt.hour >= 18]
    
    if departure_time != 'All':
        filtered_df = filtered_df[filtered_df['Departing_Time'].str.startswith(departure_time)]
    if star_rating != 'All':
        filtered_df = filtered_df[filtered_df['Star_Rating'] == star_rating]
    if seat_avail != 'All':
        filtered_df = filtered_df[filtered_df['Seat_Availability'] == seat_avail]

    # Handle Price Range Filter
    min_selected_price, max_selected_price = price_range  # Unpack selected range
    filtered_df = filtered_df[(filtered_df['Price'] >= min_selected_price) & (filtered_df['Price'] <= max_selected_price)]

    # Display Filtered Data with Clickable Links
    st.write("Filtered Data:")
    st.write(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Handle the reset button
if reset_button:
    # Reset the session state
    st.session_state.form_values = {
        'state': 'All',
        'route': 'All',
        'bus': 'All',
        'bustype': 'All',
        'departure_time': 'All',
        'rating': 'All',
        'seat_avail': 'All',
        'price_range': (0, 5000),
        'travel_date': travel_date,
       # 'travel_time': travel_time  # Reset to default price range

    }
    st.write("Form has been reset. Please interact with the app to see changes.")
