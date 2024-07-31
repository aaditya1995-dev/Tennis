import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from collections import defaultdict

print("Script started")

# Function to check availability for the existing websites
def check_availability(url):
    print(f"Starting check_availability for URL: {url}")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})

    try:
        print("Initializing WebDriver")
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully")

        print(f"Attempting to load webpage: {url}")
        driver.get(url)
        print("Webpage loaded successfully")

        print("Waiting for elements to load")
        driver.implicitly_wait(5)  # Increased wait time
        print("Wait completed")

        print("Searching for not-booked elements")
        not_booked_elements = driver.find_elements(By.CSS_SELECTOR, '.book-interval.not-booked')
        print(f"Found {len(not_booked_elements)} not-booked elements")

        if len(not_booked_elements) == 0:
            print("No not-booked elements found. Checking page source.")
            page_source = driver.page_source
            print(f"Page source length: {len(page_source)}")
            print("First 500 characters of page source:")
            print(page_source[:500])

        for element in not_booked_elements:
            try:
                print("Processing a not-booked element")
                booking_slot_element = element.find_element(By.CLASS_NAME, 'available-booking-slot')
                booking_slot = driver.execute_script("return arguments[0].textContent.trim();", booking_slot_element)
                print(f"Found booking slot: {booking_slot}")

                if booking_slot.startswith('Book at '):
                    booking_slot = booking_slot.replace('Book at ', '')
                    print(f"Trimmed booking slot: {booking_slot}")

                cost_element = element.find_element(By.CLASS_NAME, 'cost')
                cost = driver.execute_script("return arguments[0].textContent.trim();", cost_element)
                print(f"Found cost: {cost}")

                available_slots[booking_slot]['count'] += 1
                available_slots[booking_slot]['cost'] = cost
                print(f"Updated available slots: {booking_slot} - Count: {available_slots[booking_slot]['count']}, Cost: {cost}")
            except Exception as e:
                print(f"Error processing an element: {e}")

    except Exception as e:
        print(f"An error occurred in check_availability: {e}")
        st.error(f"An error occurred while processing {url}: {e}")
    finally:
        if driver:
            print("Quitting WebDriver")
            driver.quit()
            print("WebDriver quit successfully")

    print(f"Final available slots for {url}: {dict(available_slots)}")
    return available_slots


# Function to check availability for the new website
def check_availability_better(url):
    print(f"Checking availability for better.org.uk URL: {url}")
    # Set up Selenium options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialize WebDriver
    driver = webdriver.Chrome(options=options)
    print("WebDriver initialized for better.org.uk")

    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})  # Using defaultdict with nested dict

    try:
        # Load the webpage
        print(f"Attempting to load webpage: {url}")
        driver.get(url)

        # Wait for the necessary elements to load
        driver.implicitly_wait(4)  # Adjust as needed
        print("Waited for elements to load")

        # Find all elements with class 'ClassCardComponent__Row-sc-1v7d176-1'
        class_card_elements = driver.find_elements(By.CSS_SELECTOR, '.ClassCardComponent__Row-sc-1v7d176-1')
        print(f"Found {len(class_card_elements)} class card elements")

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
                print(f"Processed slot: {time_slot}, Count: {count}, Cost: {cost}")

    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")
        st.error(f"An error occurred while processing {url}: {e}")
    finally:
        # Quit the driver
        driver.quit()
        print("WebDriver quit")

    print(f"Available slots for {url}: {available_slots}")
    return available_slots


# Helper function to generate time labels
def generate_time_labels():
    return [f"{hour:02d}:00" for hour in range(7, 24)]


# Streamlit UI
print("Starting Streamlit UI")
st.title('Booking Slot Availability Checker')

# Session state to handle date and timeslot selection
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None

if 'selected_timeslot_range' not in st.session_state:
    st.session_state.selected_timeslot_range = None

# Get the current date
today = datetime.today()
print(f"Current date: {today}")

# Generate the next 7 days
next_seven_days = [(today + timedelta(days=i)).strftime("%A, %d %B") for i in range(7)]
next_seven_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
print(f"Next seven days: {next_seven_days}")

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
            print(f"Date selected: {st.session_state.selected_date}")
            st.rerun()

# If a date is selected, show the selected date and allow timeslot range selection
if st.session_state.selected_date:
    st.write(f"Selected date: **{st.session_state.selected_date_display}**")
    if st.button("Reset"):
        st.session_state.selected_date = None
        print("Date reset")
        st.rerun()

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
    print(f"Selected timeslot range: {selected_timeslot_range}")

    # Display availability based on selected date and timeslot range
    if st.button("Check Availability"):
        print(f"Checking availability for {st.session_state.selected_date_display} between {timeslot_start} - {timeslot_end}")
        st.write(
            f"Checking availability for {st.session_state.selected_date_display} between {timeslot_start} - {timeslot_end}")

        for location_name, url_template in location_urls.items():
            url = url_template.format(date=st.session_state.selected_date)
            print(f"Checking availability for {location_name}: {url}")
            if "better.org.uk" in url:
                # Check if the selected date is 7 days from now
                selected_date_obj = datetime.strptime(st.session_state.selected_date, "%Y-%m-%d")

                if selected_date_obj.date() == (today + timedelta(days=6)).date():
                    print(f"{location_name} has not released booking slots for {st.session_state.selected_date_display} yet.")
                    st.write(f"{location_name} has not released booking slots for {st.session_state.selected_date_display} yet.")
                    continue

                available_slots = check_availability_better(url)
            else:
                available_slots = check_availability(url)

            # Filter availability based on selected timeslot range
            filtered_slots = {}
            for slot in available_slots:
                hour = int(slot.split(':')[0])
                if selected_timeslot_range[0] <= hour < selected_timeslot_range[1]:
                    filtered_slots[slot] = available_slots[slot]

            print(f"Filtered slots for {location_name}: {filtered_slots}")

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
                print(f"No available slots found for {location_name}")
                st.write(f"No available slots found for {location_name}.")

print("Script completed")