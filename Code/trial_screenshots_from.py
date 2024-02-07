from webdata import webdriver
from PIL import Image
import requests

# Set up Selenium with the appropriate web driver
driver = webdriver.Chrome('path/to/chromedriver')

# Navigate to the login website
driver.get('https://admin.pcmcsmartsarathi.org/#/login')

# Fill in login credentials
driver.find_element()
# username_input = driver.find_element_by_id('Foxberry')
# password_input = driver.find_element_by_id('pcmc1234')
# username_input.send_keys('your_username')
# password_input.send_keys('your_password')

# Take a screenshot
driver.save_screenshot('login_page.png')

# Send an API request to receive OTP
registered_mobile_number = 'your_mobile_number'
website_url = 'https://example.com/login'
api_url = 'https://api.example.com/otp'
response = requests.post(api_url, json={'mobile_number': registered_mobile_number, 'website_url': website_url})

# # Retrieve the OTP from the response
# otp = response.json()['otp']
#
# # Continue the login process by entering the OTP
# otp_input = driver.find_element_by_id('otp')
# otp_input.send_keys(otp)
#
# # Take another screenshot after entering the OTP
# driver.save_screenshot('otp_page.png')
#
# # Perform further actions as needed
#
# # Close the browser
# driver.quit()
