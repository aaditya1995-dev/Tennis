import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from collections import defaultdict


# Function to check availability for the existing websites
def check_availability(url):
    # Set up Selenium options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialize WebDriver
    driver = webdriver.Chrome(options=options)

    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})  # Using defaultdict with nested dict

    try:
        # Load the webpage
        driver.get(url)

        # Wait for the necessary elements to load
        driver.implicitly_wait(2)  # Adjust as needed

        # Find all elements with class 'book-interval not-booked'
        not_booked_elements = driver.find_elements(By.CSS_SELECTOR, '.book-interval.not-booked')

        # Process each found element
        for element in not_booked_elements:
            booking_slot_element = element.find_element(By.CLASS_NAME, 'available-booking-slot')
            booking_slot = driver.execute_script("return arguments[0].textContent.trim();", booking_slot_element)

            # Trim 'Book at ' prefix
            if booking_slot.startswith('Book at '):
                booking_slot = booking_slot.replace('Book at ', '')

            # Extract cost information
            cost_element = element.find_element(By.CLASS_NAME, 'cost')
            cost = driver.execute_script("return arguments[0].textContent.trim();", cost_element)

            available_slots[booking_slot]['count'] += 1
            available_slots[booking_slot]['cost'] = cost

    except Exception as e:
        st.error(f"An error occurred while processing {url}: {e}")
    finally:
        # Quit the driver
        driver.quit()

    return available_slots


# Function to check availability for the new website
def check_availability_better(url):
    # Set up Selenium options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialize WebDriver
    driver = webdriver.Chrome(options=options)

    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})  # Using defaultdict with nested dict

    try:
        # Load the webpage
        driver.get(url)

        # Wait for the necessary elements to load
        driver.implicitly_wait(4)  # Adjust as needed

        # Find all elements with class 'ClassCardComponent__Row-sc-1v7d176-1'
        class_card_elements = driver.find_elements(By.CSS_SELECTOR, '.ClassCardComponent__Row-sc-1v7d176-1')

        # Process each found element
        for element in class_card_elements:
            time_element = element.find_element(By.CLASS_NAME, 'ClassCardComponent__ClassTime-sc-1v7d176-3')
            time_slot = driver.execute_script("return arguments[0].textContent.trim();", time_element)

            cost_element = element.find_element(By.CLASS_NAME, 'ClassCardComponent__Price-sc-1v7d176-14')
            cost = driver.execute_script("return arguments[0].textContent.trim();", cost_element)

            spaces_element = element.find_element(By.CSS_SELECTOR, '.ContextualComponent__BookWrap-sc-eu3gk6-1')
            spaces_text = driver.execute_script("return arguments[0].textContent.trim();", spaces_element)

            # Extract the number of spaces available
            count = int(spaces_text.split()[0])  # Extract the integer value

            if count > 0:
                available_slots[time_slot]['count'] = count
                available_slots[time_slot]['cost'] = cost

    except Exception as e:
        st.error(f"An error occurred while processing {url}: {e}")
    finally:
        # Quit the driver
        driver.quit()

    return available_slots


# Helper function to generate time labels
def generate_time_labels():
    return [f"{hour:02d}:00" for hour in range(7, 24)]


# Streamlit UI
st.title('Booking Slot Availability Checker')

# Session state to handle date and timeslot selection
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None

if 'selected_timeslot_range' not in st.session_state:
    st.session_state.selected_timeslot_range = None

# Get the current date
today = datetime.today()

# Generate the next 7 days
next_seven_days = [(today + timedelta(days=i)).strftime("%A, %d %B") for i in range(7)]
next_seven_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

# Dictionary to map URLs to location names (including query parameters)
location_urls = {
    "Regent's Park": "https://regents.parksports.co.uk/Booking/BookByDate#?date={date}&role=guest",
    "Kennington Park": "https://clubspark.lta.org.uk/kenningtonpark/Booking/BookByDate#?date={date}&role=guest",
    "Tanner St. Park": "https://clubspark.lta.org.uk/TannerStPark/Booking/BookByDate#?date={date}&role=guest",
    "Islington Tennis Centre (Indoor)": "https://bookings.better.org.uk/location/islington-tennis-centre/tennis-court-indoor/{date}/by-time",
    "Islington Tennis Centre (Outdoor)": "https://bookings.better.org.uk/location/islington-tennis-centre/tennis-court-outdoor/{date}/by-time"
}

# Display buttons for each of the next 7 days if no date is selected
if st.session_state.selected_date is None:
    st.write("Select a date to check availability:")
    for i, day in enumerate(next_seven_days):
        if st.button(day):
            st.session_state.selected_date = next_seven_dates[i]
            st.session_state.selected_date_display = next_seven_days[i]
            st.experimental_rerun()

# If a date is selected, show the selected date and allow timeslot range selection
if st.session_state.selected_date:
    st.write(f"Selected date: **{st.session_state.selected_date_display}**")
    if st.button("Reset"):
        st.session_state.selected_date = None
        st.experimental_rerun()

    # Allow the user to select a timeslot range using a select_slider
    st.write("Select a timeslot range:")
    time_labels = generate_time_labels()
    timeslot_start, timeslot_end = st.select_slider(
        "",
        options=time_labels,
        value=(time_labels[0], time_labels[-1])
    )

    # Convert selected timeslot range to integers for processing
    selected_timeslot_range = (int(timeslot_start.split(':')[0]), int(timeslot_end.split(':')[0]))
    st.session_state.selected_timeslot_range = selected_timeslot_range

    # Display availability based on selected date and timeslot range
    if st.button("Check Availability"):
        st.write(
            f"Checking availability for {st.session_state.selected_date_display} between {timeslot_start} - {timeslot_end}")

        for location_name, url_template in location_urls.items():
            url = url_template.format(date=st.session_state.selected_date)
            if "better.org.uk" in url:
                available_slots = check_availability_better(url)
            else:
                available_slots = check_availability(url)

            # Filter availability based on selected timeslot range
            filtered_slots = {}
            for slot in available_slots:
                hour = int(slot.split(':')[0])
                if selected_timeslot_range[0] <= hour < selected_timeslot_range[1]:
                    filtered_slots[slot] = available_slots[slot]

            if filtered_slots:
                with st.container():
                    st.markdown(f"### {location_name}")
                    for slot, info in sorted(filtered_slots.items()):
                        count = info['count']
                        cost = info['cost']
                        if cost is not None:
                            st.markdown(
                                f"**{slot}** &nbsp;&nbsp; <span style='color:grey;'>{count} court(s) available, Cost: {cost}</span> &nbsp;&nbsp;"
                                f"<a href='{url}' style='background-color:green; color:white; padding:5px 10px; text-decoration:none; border-radius:5px;'>Book</a>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"**{slot}** &nbsp;&nbsp; <span style='color:grey;'>{count} court(s) available</span> &nbsp;&nbsp;"
                                f"<a href='{url}' style='background-color:green; color:white; padding:5px 10px; text-decoration:none; border-radius:5px;'>Book</a>",
                                unsafe_allow_html=True
                            )
            else:
                st.write(f"No available slots found for {location_name}.")
