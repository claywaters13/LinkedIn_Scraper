import os
import time
import pickle

from Helper_Interfaces.Web_Interface.WebInterface import WebInterface


class LinkedInInterface(WebInterface):
    def __init__(self):
        super().__init__()
        self.linkedin_cookie_path = f'{os.getcwd()}/Helper_Interfaces/LinkedIn_Interface/linkedin_cookie/cookie.pkl'
        print(self.linkedin_cookie_path)
        self.linkedin_cookie_timeout = 1  # Day
        self.check_cookie()
        self.logged_in_webdriver = None
        self.login_and_save_webdriver()

    def login_and_save_webdriver(self):
        self.update_webdriver()
        self.logged_in_webdriver = self.webdriver
        self.logged_in_webdriver.get('https://www.linkedin.com/login')
        self.load_cookie()
        self.logged_in_webdriver.get('https://www.linkedin.com/login')

    def check_cookie(self):
        cookie_creation_time = os.stat(self.linkedin_cookie_path).st_mtime
        cookie_age_d = (time.time() - cookie_creation_time) / 60 / 60 / 24
        print("Checking LinkedIn Cookie Status")
        print(f"Most recent cookie is {cookie_age_d} days old")
        if cookie_age_d < 1:
            print("Cookie is less than 1 day old. Continuing script with existing cookie")
        else:
            print("Would you like to update the cookie (Y/N)")
            get_another_cookie = input()
            if get_another_cookie == "Y" or get_another_cookie == "y":
                print("Starting cookie gathering sequence")
                self.login_and_save_cookie()
            else:
                print("Continuing script with existing cookie")

    def login_and_save_cookie(self):
        # create webdriver, load login page, and wait for user input
        self.update_webdriver()
        driver = self.webdriver
        driver.get('https://www.linkedin.com/login')
        print("Log into LinkedIn, come back to the python console, and hit any key to save the cookie")
        foo = input()

        # save cookie
        self.save_cookie(driver, self.linkedin_cookie_path)
        print("cookie saved in tmp folder")

    def save_cookie(self, driver, path):
        with open(path, 'wb') as filehandler:
            pickle.dump(driver.get_cookies(), filehandler)

    def load_cookie(self):
        with open(self.linkedin_cookie_path, 'rb') as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.logged_in_webdriver.add_cookie(cookie)

    def get_company_linkedin_info(self, company_name, company_urls):

        # preparing response
        details = {}

        # only try to find the business if there is at least one company URL
        if len(company_urls) == 0:
            # No url provided, so we don't want to check this
            print("no URL for this account")
            return details

        # See if we can find the company
        print(f"\nStarted search for {company_name} with website {company_urls}")
        # get a list of potential URLs for a company
        potential_urls = self.get_company_urls_from_search(company_name)
        print("found these potential URLs from LinkedIn Search", potential_urls)

        # add number of search results to response
        details['num_LinkedIn_search_results'] = len(potential_urls)

        for url in potential_urls:
            # navigate to company about page
            self.logged_in_webdriver.get(f'{url}/about/')

            # wait on page to load
            time.sleep(0.5)

            if self.check_for_right_url(company_urls=company_urls):
                # We've found a business with the right URL
                print("Successfully found company with matching URL", company_name, url,
                      "-----------------------------")
                # Get all company information and return
                details.update(self.get_company_details_from_webdriver_at_about_page_linkedin())
                break

            else:
                print("Couldn't match URL", company_name, url)

        return details

    def get_company_urls_from_search(self, company_name, max_count=5):
        # Load Activity Calendar
        company_name = company_name.replace(" ", '%20')
        search_url = f'https://www.linkedin.com/search/results/companies/?keywords={company_name}'
        self.logged_in_webdriver.get(search_url)

        # wait for the page to load
        time.sleep(0.5)

        # find all elements that have links
        elems = self.webdriver.find_elements_by_xpath("//a[@href]")

        # iterate though all elements with links and add them to a list if they are a company link
        url_list = []
        for elem in elems:
            url = elem.get_attribute("href")
            if len(url_list) < max_count:
                if url.startswith("https://www.linkedin.com/company/"):
                    if "company/linkedin" not in url:
                        if url not in url_list:
                            url_list.append(url)

        return url_list

    def check_for_right_url(self,  company_urls):

        # Find location fields in the about page for the company
        potential_urls = self.logged_in_webdriver.find_elements_by_xpath("//a[@href]")

        # iterate though all elements with links and add them to a list if they are a company link
        for linked_in_url in potential_urls:
            if "http://" in linked_in_url.text:
                for company_url in company_urls:
                    if linked_in_url.text in company_url or company_url in linked_in_url.text:
                        # there is a direct match with the company provided url and the LinkedIn URL
                        return True

        return False

    def get_company_details_from_webdriver_at_about_page_linkedin(self):

        # Create empty dict to add to
        company_details = {}

        # Get all information from LinkedIn

        try:
            # Find information
            company_details['LinkedIn Overview'] = self.logged_in_webdriver.find_element_by_xpath(
                "//*[contains(@id, 'ember')]/section/p").text
        except:
            pass

        try:
            title_list = []
            summary_titles = self.logged_in_webdriver.find_elements_by_xpath("//*[contains(@id, 'ember')]/section/dl/dt")
            for i, item in enumerate(summary_titles):
                title_list.append(item.text)

            values_list = []
            summary_values = self.logged_in_webdriver.find_elements_by_xpath("//*[contains(@id, 'ember')]/section/dl/dd")
            for i, item in enumerate(summary_values):
                values_list.append(item.text)

            offset = 0

            for i, title in enumerate(title_list):
                try:
                    # company size needs to be handled differently since it might have 1 or 2 fields
                    if title == "Company size":
                        company_details['LinkedIn Company Size Range'] = values_list[i].split(" ")[0]
                        if "LinkedIn" in values_list[i + 1]:
                            company_details["Employees on LinkedIn"] = values_list[i + 1].split(" ")[0]
                            offset = 1
                    else:
                        modified_title = f"LinkedIn {title}"
                        company_details[modified_title] = values_list[i + offset]
                except:
                    pass
        except:
            pass

        return company_details