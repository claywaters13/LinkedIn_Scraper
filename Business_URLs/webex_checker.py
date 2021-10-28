from selenium import webdriver
import pandas as pd
from pathlib import Path
import time


from Business_URLs.business_search_interface import  get_resolved_domain

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
        x = 1 / 0
    account_list_path = f"{dir}/Inputs/account_list.csv"
elif starting_file == "Modified":
    account_list_path = f"{dir}/Outputs/modified_account_list.csv"

account_list_df = pd.read_csv(account_list_path).set_index('Account Name')

# create web driver
opts = webdriver.ChromeOptions()
opts.headless = False
driver = webdriver.Chrome('../login_tools/chromedriver', options=opts)
driver.set_page_load_timeout(8)

# Iterate through accounts and the resolved domain
for account in account_list_df.index:

    try:
        # Filter to process account websites that exist
        if account_list_df.at[account, 'Domain'] == account_list_df.at[account, 'Domain']:

            # Retrieve the URL from the dataframe for this account
            url_from_salesforce = account_list_df.at[account, 'Domain']
            webex_check_url_from_salesforce = url_from_salesforce.replace(".", ".webex.")
            webex_check_url_from_salesforce = f'http://{webex_check_url_from_salesforce}'

            # webex_check_url_from_salesforce = 'http://cdlschool.webex.com'
            # print(f"\nChecking if {account} has webex site set up ({webex_check_url_from_salesforce})")
            driver.get(webex_check_url_from_salesforce)
            success = driver.find_element_by_class_name('join-input')
            if success:
                print("We found one!!!", account, url_from_salesforce)
                time.sleep(1)
            time.sleep(1)


            # # Save csv to outputs
            # output_file_path = f"{dir}/Outputs/modified_account_list.csv"
            # account_list_df.to_csv(output_file_path)
            # print("successfully updated csv")

    except:
        # print("this lookup failed for some reason")
        pass
