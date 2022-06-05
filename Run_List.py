"""
This script is what to run for the full data processing job.  It will enable command prompts to walk you
fully through:
 - Logging in manually and Saving a cookie
 - Loading an Input List
 - Checking if a partial output list exists and creating one if needed
 - Getting LinkedIn URLs
 - Verifying a website doesn't redirect
 - Getting LinkedIn Information for each Account
"""

import os
import time
from datetime import datetime
import pandas as pd

from Helper_Interfaces.Web_Interface.WebInterface import WebInterface
from Helper_Interfaces.WebEx_Interface.WebExInterface import WebExInterface
from Helper_Interfaces.LinkedIn_Interface.LinkedInInterface import LinkedInInterface

# ----------------------------------------------------------------
#
# Configuration
#
# ----------------------------------------------------------------

job_name = "June_22_Updates_Sandy"

check_website_redirects = True
find_linkedin_urls = True
find_linkedin_details = True
check_webex_websites = True

salesforce_account_name = "Account Name"
salesforce_domain = "Domain Key"

# ----------------------------------------------------------------
#
# Initialization Script
#
# ----------------------------------------------------------------

# Create Web Interface
WebInterface = WebInterface()
WebExInterface = WebExInterface()
LinkedInInterface = LinkedInInterface()

# -----------------------
# Getting the List
# -----------------------

print("----------------------------------------------------------------")
list_location = f"Jobs/{job_name}/Acct_List/account_list.csv"
print("Checking List Status")
print("Retrieving list from this location:  ", list_location)

if os.path.exists(list_location):
    list_creation_time = os.stat(list_location).st_mtime
    list_age_d = (time.time() - list_creation_time) / 60 / 60 / 24
    print(f"Most recent list is {list_age_d:.2f} days old")
    account_list = pd.read_csv(list_location)

else:
    print("List not retrievable at this location  ", list_location)
    print("Make sure the input list is at this exact folder location")


# See if any websites have been loaded yet
needed_status_cols = ['Website_Loaded', 'Checked_for_WebEx_Site', 'Searched_LinkedIn']
for col in needed_status_cols:
    if col not in account_list:
        account_list[col] = ""

# ----------------------------------------------------------------
#
# Initialization Script
#
# ----------------------------------------------------------------

print("----------------------------------------------------------------")
print(f"Iterating through {len(account_list)} accounts to get information")

start_time = datetime.now()

for i, row in account_list.iterrows():
    try:
        acct_name = row[salesforce_account_name]
        original_domain = row[salesforce_domain]
        print(f"-------"*10, "\n")
        percentage = (i+1)/int(len(account_list))
        print(f"Processing Account: {i+1}/{len(account_list)}     {percentage:.0%}")
        print("Time Elapsed: ", (datetime.now() - start_time))
        print(f"acct info: {acct_name}, {original_domain}")

        # Track if we actually did anything
        did_something_useful = False

        # Check for website redirects
        if original_domain == original_domain and row['Website_Loaded'] != True:
            did_something_useful = True
            # Get Data
            print('\nChecking Website Redirects')
            redirect_response = WebInterface.get_redirected_domain(original_domain)
            print('Redirect Information: ', redirect_response)

            # Update Dataframe with Redirection Information
            for item in redirect_response:
                # Add column if it doesn't exist
                if item not in account_list:
                    account_list[item] = ""

                # Add data to this column
                account_list.at[i, item] = redirect_response[item]

        # Check if WebEx site exists
        if original_domain == original_domain and (not row['Checked_for_WebEx_Site'] or did_something_useful):
            did_something_useful = True

            # Get Data
            print('\nChecking for WebEx Site')
            domains = account_list.at[i, 'All_Domains']

            print("domains equal ", domains)
            webex_response = WebExInterface.check_for_webex_site(domains)
            print('WebEx Information:, ', webex_response)

            # Update Dataframe with Redirection Information
            for item in webex_response:
                # Add column if it doesn't exist
                if item not in account_list:
                    account_list[item] = ""

                # Add data to this column
                account_list.at[i, item] = webex_response[item]

        # Check if LinkedIn Has this Business and get Information if Possible
        if not row['Searched_LinkedIn'] or did_something_useful:
            did_something_useful = True
            print("\nGetting Business URLs from LinkedIn")
            linkedin_response = LinkedInInterface.get_company_linkedin_info(company_name=acct_name, company_urls=domains)
            print('LinkedIn Information: ', linkedin_response)

            # Update Dataframe with WebEx Response Information
            # Update Dataframe with Redirection Information
            for item in linkedin_response:
                # Add column if it doesn't exist
                if item not in account_list:
                    account_list[item] = ""

                # Add data to this column
                account_list.at[i, item] = linkedin_response[item]

        print("\nFinal Data Compiled")
        print(account_list.iloc[[i]].to_string())

        # Save List to csv
        account_list.to_csv(list_location, index=False)
        print("Updated CSV")

        # Sleep for a few
        if did_something_useful:
            time.sleep(5)

    except:
        print("SOMETHING WENT PRETTY WRONG", "_*-"*100)
        time.sleep(2)
        pass


