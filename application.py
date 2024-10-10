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
cursor.execute("use redbus_project")

# Load CSV Data
df = pd.read_sql('SELECT * FROM 'Bus_routes', conn)

# Clean the 'Price' column: Remove non-numeric characters and convert to numeric
df['Price'] = df['Price'].replace('[\$,]', '', regex=True)  # Remove any commas or dollar signs if present
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')  # Convert to numeric, set non-convertibles to NaN

# Ensure 'route_link' is present in the DataFrame
if 'Route_Link' in df.columns:
    # Create HTML links in the DataFrame
    df['route_link'] = df['Route_Link'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
else:
    st.error("The 'route_link' column is missing in the CSV file.")

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

# Initialize session state if not already set
if 'form_values' not in st.session_state:
    st.session_state.form_values = {
        'route': 'All',
        'bus': 'All',
        'bustype': 'All',
        'departure_time': 'All',
        'rating': 'All',
        'seat_avail': 'All',
        'price_range': 'All'
    }

# Define a form to hold the input elements and buttons
with st.form(key='filter_form'):
    # Route Name Selection
    route_name = ['All'] + df['Route_Name'].drop_duplicates().tolist()
    routename = st.selectbox("Select your route:", route_name, key='route', index=route_name.index(st.session_state.form_values['route']))

    # Bus Name Selection
    bus_name = ['All'] + df['Bus_Name'].drop_duplicates().tolist()
    busname = st.selectbox("Select your bus:", bus_name, key='bus', index=bus_name.index(st.session_state.form_values['bus']))

    # Bus Type Selection
    bus_type = ['All'] + df['Bus_Type'].drop_duplicates().tolist()
    bustype = st.selectbox("Select your bus type:", bus_type, key='bustype', index=bus_type.index(st.session_state.form_values['bustype']))

    # Departing Time Selection
    unique_times = ["All", "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00",
                    "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", 
                    "21:00", "22:00", "23:00"]
    departure_time = st.selectbox("Select your departure time:", unique_times, key='departure_time', index=unique_times.index(st.session_state.form_values['departure_time']))

    # Star Rating Selection
    rating = ['All', '*', '**', '***', '****', '*****']
    star_rating = st.selectbox("Select your star rating:", rating, key='rating', index=rating.index(st.session_state.form_values['rating']))

    # Seat Availability Selection
    seat_availability = ['All'] + df['Seat_Availability'].drop_duplicates().tolist()
    seat_avail = st.selectbox("Select your seat availability:", seat_availability, key='seat_avail', index=seat_availability.index(st.session_state.form_values['seat_avail']))

    # Price Range Selection as Dropdown
    price_ranges = ['All', 'INR 0 - 500', 'INR 500 - 1000', 'INR 1000 - 1500', 'INR 1500 - 2000', 'INR 2000+']
    selected_price_range = st.selectbox("Select your price range:", price_ranges, key='price_range', index=price_ranges.index(st.session_state.form_values['price_range']))

    # Create a Submit and Reset Button
    submit_button = st.form_submit_button(label='Submit')
    reset_button = st.form_submit_button(label='Reset')

# Handle the form submission
if submit_button:
    # Save the current values to session state
    st.session_state.form_values = {
        'route': routename,
        'bus': busname,
        'bustype': bustype,
        'departure_time': departure_time,
        'rating': star_rating,
        'seat_avail': seat_avail,
        'price_range': selected_price_range
    }

    # Filter Data
    filtered_df = df.copy()
    
    if routename != 'All':
        filtered_df = filtered_df[filtered_df['Route_Name'] == routename]
    if busname != 'All':
        filtered_df = filtered_df[filtered_df['Bus_Name'] == busname]
    if bustype != 'All':
        filtered_df = filtered_df[filtered_df['Bus_Type'] == bustype]
    if departure_time != 'All':
        filtered_df = filtered_df[filtered_df['Departing_Time'] == departure_time]
    if star_rating != 'All':
        filtered_df = filtered_df[filtered_df['Star_Rating'] == star_rating]
    if seat_avail != 'All':
        filtered_df = filtered_df[filtered_df['Seat_Availability'] == seat_avail]

    # Handle Price Range Filter
    if selected_price_range != 'All':
        min_price, max_price = 0, float('inf')  # Set default min and max prices
        if selected_price_range == 'INR 0 - 500':
            min_price, max_price = 0, 500
        elif selected_price_range == 'INR 500 - 1000':
            min_price, max_price = 500, 1000
        elif selected_price_range == 'INR 1000 - 1500':
            min_price, max_price = 1000, 1500
        elif selected_price_range == 'INR 1500 - 2000':
            min_price, max_price = 1500, 2000
        elif selected_price_range == 'INR 2000+':
            min_price = 2000
        filtered_df = filtered_df[(filtered_df['Price'] >= min_price) & (filtered_df['Price'] <= max_price)]

    # Display Filtered Data with Clickable Links
    st.write("Filtered Data:")
    st.write(filtered_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Handle the reset button
if reset_button:
    # Reset the session state
    st.session_state.form_values = {
        'route': 'All',
        'bus': 'All',
        'bustype': 'All',
        'departure_time': 'All',
        'rating': 'All',
        'seat_avail': 'All',
        'price_range': 'All'
    }
    st.write("Form has been reset. Please interact with the app to see changes.")
