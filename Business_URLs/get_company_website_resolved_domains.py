from selenium import webdriver
import pandas as pd
from pathlib import Path


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
opts.headless = True
driver = webdriver.Chrome('../login_tools/chromedriver', options=opts)
driver.set_page_load_timeout(5)

# Iterate through accounts and the resolved domain
for account in account_list_df.index:

    try:
        # Filter to process account websites that exist
        if account_list_df.at[account, 'Domain'] == account_list_df.at[account, 'Domain']:

            # Filter out accounts that have already been run successfully
            current_output_test = account_list_df.at[account, 'Website Redirected']
            if current_output_test != "True" and current_output_test != "False":

                # Retrieve the URL from the dataframe for this account
                url_from_salesforce = account_list_df.at[account, 'Domain']
                print(f"\nChecking if {account} website ({url_from_salesforce}) resolves to a different domain")

                # Visit this url and see what domain it lands on
                resolved_url = get_resolved_domain(url_from_salesforce)

                if resolved_url == None:
                    print("Unable to load webpage", resolved_url)
                    account_list_df.loc[account, 'Website Redirected'] = "unable to load webpage"
                    account_list_df.loc[account, 'New Website Domain'] = "unable to load webpage"

                # If it lands on a new domain, save that it was redirected and save the new domain
                elif url_from_salesforce != resolved_url:
                    print("It resolved at a new url: ", resolved_url,
                          "--------------------------------------------------")
                    account_list_df.loc[account, 'Website Redirected'] = True
                    account_list_df.loc[account, 'New Website Domain'] = resolved_url

                # Else just save that we weren't directed
                else:
                    print("It resolved at the same URL")
                    account_list_df.loc[account, 'Website Redirected'] = False

                # Save csv to outputs
                output_file_path = f"{dir}/Outputs/modified_account_list.csv"
                account_list_df.to_csv(output_file_path)
                print("successfully updated csv")

    except:
        print("this lookup failed for some reason")
        pass
