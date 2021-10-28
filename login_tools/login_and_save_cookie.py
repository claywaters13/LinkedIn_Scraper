from selenium import webdriver
import os

from cookie_management_interface import save_cookie


# direct the webdriver to where the browser file is:
driver_path = "chromedriver"
driver = webdriver.Chrome(executable_path=driver_path)

# create webdriver, load login page, and wait for user input
driver = webdriver.Chrome('chromedriver')
driver.get('https://www.linkedin.com/login')
print("Log into LinkedIn, come back to the python console, and hit any key to save the cookie")
foo = input()

# set path for where to save the cookie
current_directory = os.getcwd()
temp_folder_dir = "tmp"
path = os.path.join(current_directory, temp_folder_dir)

# save cookie
save_cookie(driver, f'{path}/cookie.pkl')
print("cookie saved in tmp folder")