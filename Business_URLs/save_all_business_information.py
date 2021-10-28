from selenium import webdriver
import time
import pandas as pd
from pathlib import Path

from login_tools.cookie_management_interface import load_cookie
from Business_URLs.business_search_interface import get_company_linkedin_page, get_company_details_from_linkedin


# Config ---------------------------------
# Two options for where to start
# Original - starts with the original file and creates a new output file or overwrites it
# Modified - Starts with output file and modifies it further
starting_file = "Modified"

# get parent directory
dir = Path(__file__).parent.parent

# Load list of all companies based on configuration
if starting_file == "Original":
    print("Waring, this will overwrite any output file located in the output folder")
    print("Type 'Yes' and press enter to Continue")
    input = input()
    if input != "Yes":
        x = 1/0
    account_list_path = f"{dir}/Inputs/account_list.csv"
elif starting_file == "Modified":
    account_list_path = f"{dir}/Outputs/modified_account_list.csv"

account_list_df = pd.read_csv(account_list_path).set_index('Account Name')

# Set path to cookies and create web driver
cookie_path = f"{dir}/login_tools/tmp/cookie.pkl"
opts = webdriver.ChromeOptions()
opts.headless = True
driver = webdriver.Chrome('../login_tools/chromedriver', options=opts)
driver.set_page_load_timeout(5)

# Load LinkedIn and load cookies with login info
driver.get('https://www.linkedin.com/login')
load_cookie(driver, cookie_path)
time.sleep(1)

# Iterate through accounts and get information
for account in account_list_df.index:
    try:
        company_linkedin_url = account_list_df.at[account, 'Confirmed LinkedIn URL']

        # Filter to process accounts that have a valid LinkedIn Link
        if "www." in str(company_linkedin_url):
            # Load this business page on LinkedIn
            company_details = get_company_details_from_linkedin(driver=driver, company_linkedin_url=company_linkedin_url)
            for key, value in company_details.items():
                account_list_df.at[account, key] = value

            account_list_df.to_csv(f"{dir}/Outputs/modified_account_list_with_details.csv")
            print("Saved values to csv")

    except:
        print("Something went very wrong with ", account)



