import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Function to check availability
def check_availability(url):
    # Set up Selenium options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialize WebDriver
    driver = webdriver.Chrome(options=options)

    available_slots = []

    try:
        # Load the webpage
        driver.get(url)

        # Wait for the necessary elements to load
        driver.implicitly_wait(3)  # Adjust as needed

        # Find all elements with class 'book-interval not-booked'
        not_booked_elements = driver.find_elements(By.CSS_SELECTOR, '.book-interval.not-booked')

        # Process each found element
        for element in not_booked_elements:
            href = element.get_attribute('href')
            cost = element.find_element(By.CLASS_NAME, 'cost').text

            booking_slot_element = element.find_element(By.CLASS_NAME, 'available-booking-slot')
            booking_slot = driver.execute_script("return arguments[0].textContent;", booking_slot_element)
            available_slots.append((booking_slot, href))

    except Exception as e:
        st.error(f"An error occurred while processing {url}: {e}")
    finally:
        # Quit the driver
        driver.quit()

    return available_slots

# Streamlit UI
st.title('Booking Slot Availability Checker')

# Input date from the user
date = st.text_input("Enter the date you want to search for (YYYY-MM-DD):")

# Define URLs to check
urls = [
    f"https://regents.parksports.co.uk/Booking/BookByDate?date={date}#?date={date}&role=guest",
    f"https://clubspark.lta.org.uk/kenningtonpark/Booking/BookByDate#?date={date}&role=guest"
]

# Check availability button
if st.button("Check Availability"):
    for url in urls:
        available_slots = check_availability(url)
        if available_slots:
            st.write(f"Available Slots for {url}:")
            for index, (slot, href) in enumerate(available_slots, start=1):
                st.write(f"Slot {index}:")
                st.write(f"  - Booking Slot: {slot}")
                st.write(f"  - Href: [Link]({href})")
                st.write("")  # Blank line for readability
        else:
            st.write(f"No available slots found for {url}.")
