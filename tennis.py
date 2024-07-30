import streamlit as st
from seleniumbase import SB
from datetime import datetime, timedelta
from collections import defaultdict

# Function to check availability for the existing websites
def check_availability(url):
    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})

    with SB(uc=True, headless=True) as sb:
        try:
            sb.get(url)
            sb.wait_for_element('.book-interval.not-booked', timeout=10)

            not_booked_elements = sb.find_elements('.book-interval.not-booked')

            for element in not_booked_elements:
                booking_slot = sb.execute_script("return arguments[0].querySelector('.available-booking-slot').textContent.trim();", element).replace('Book at ', '')
                cost = sb.execute_script("return arguments[0].querySelector('.cost').textContent.trim();", element)

                available_slots[booking_slot]['count'] += 1
                available_slots[booking_slot]['cost'] = cost

        except Exception as e:
            st.error(f"An error occurred while processing {url}: {e}")

    return available_slots

# Function to check availability for the new website
def check_availability_better(url):
    available_slots = defaultdict(lambda: {'count': 0, 'cost': None})

    with SB(uc=True, headless=True) as sb:
        try:
            sb.get(url)
            sb.wait_for_element('.ClassCardComponent__Row-sc-1v7d176-1', timeout=10)

            class_card_elements = sb.find_elements('.ClassCardComponent__Row-sc-1v7d176-1')

            for element in class_card_elements:
                time_slot = sb.execute_script("return arguments[0].querySelector('.ClassCardComponent__ClassTime-sc-1v7d176-3').textContent.trim();", element)
                cost = sb.execute_script("return arguments[0].querySelector('.ClassCardComponent__Price-sc-1v7d176-14').textContent.trim();", element)
                spaces_text = sb.execute_script("return arguments[0].querySelector('.ContextualComponent__BookWrap-sc-eu3gk6-1').textContent.trim();", element)

                count = int(spaces_text.split()[0])

                if count > 0:
                    available_slots[time_slot]['count'] = count
                    available_slots[time_slot]['cost'] = cost

        except Exception as e:
            st.error(f"An error occurred while processing {url}: {e}")

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
                # Check if the selected date is 7 days from now
                selected_date_obj = datetime.strptime(st.session_state.selected_date, "%Y-%m-%d")

                if selected_date_obj.date() == (today + timedelta(days=6)).date():
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