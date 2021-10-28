from selenium import webdriver
import time
import pandas as pd
from pathlib import Path

from login_tools.cookie_management_interface import load_cookie
from Business_URLs.business_search_interface import get_company_linkedin_page


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

# Remove duplicates
account_list_df = account_list_df.drop_duplicates()

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
    # Filter to process accounts that we haven't already searched for
    if account_list_df.at[account, 'Looked for this on LinkedIn'] is not True:

        try:
            # Search LinkedIn for this business/account
            state = account_list_df.at[account, 'Billing State']
            company_url = account_list_df.at[account, 'Domain']
            num_search_results, confirmed_linkedin_url = get_company_linkedin_page(
                driver=driver,
                company_name=account,
                company_url=company_url,
                state=state
            )

            # Update results based on the search

            # Mark this site as 'looked for'
            account_list_df.loc[account, 'Looked for this on LinkedIn'] = True

            # Add the number of search results for QA
            account_list_df.loc[account, 'Num Search Results'] = num_search_results

            # Add the confirmed URL that we have
            account_list_df.loc[account, 'Confirmed LinkedIn URL'] = confirmed_linkedin_url

            # Save csv to outputs
            output_file_path = f"{dir}/Outputs/modified_account_list.csv"
            account_list_df.to_csv(output_file_path)
            print("successfully updated csv")

        except:
            print("this lookup failed for some reason")
            pass
