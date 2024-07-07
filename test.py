from bs4 import BeautifulSoup

# Example HTML snippet
html = '''
<div class="resource-session" data-payment-type="cash" data-availability="true" data-max-slots-doubles="0" data-max-slots-singles="0" data-resource-interval="60" data-session-id="fbfa0755-24a8-4700-9a95-b9dda8e89fc5" data-capacity="1" data-end-time="480" data-start-time="420" data-slot-key="92fd3be1-3a82-4c30-a418-3263ccecad70fbfa0755-24a8-4700-9a95-b9dda8e89fc5420" data-session-cost="18.65" data-cost-from="18.65" data-session-member-cost="0" data-session-guest-cost="0">
    <div class="resource-interval" data-system-start-time="420" data-system-end-time="480" style="height: 120px">
        <a class="book-interval not-booked" href="#" data-test-id="booking-92fd3be1-3a82-4c30-a418-3263ccecad70|2024-06-29|420">
            <span class="cost">£18.65</span>
            <span class="available-booking-slot">Book at 07:00 - 08:00</span> 
        </a>
    </div>
    <div class="session-break "></div>
</div>
'''

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Extract session details
session_div = soup.find('div', class_='resource-session')

if session_div:
    # Check availability
    availability = session_div.get('data-availability', '')
    if availability == 'true':
        # Extract start time
        start_time = session_div.get('data-start-time', '')

        # Extract booking URL
        booking_url = session_div.find('a', class_='book-interval').get('href', '')

        # Print or use the extracted data
        print(f"Start Time: {start_time}")
        print(f"Booking URL: {booking_url}")
    else:
        print("Session not available")
else:
    print("Session not found")
