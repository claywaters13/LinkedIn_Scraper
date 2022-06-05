import time
from urllib.parse import urlparse
from pathlib import Path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class WebInterface:
    def __init__(self):
        self.browser_load_timeout = 5
        self.chromedriver_path = f"{Path(__file__).parent}/chromedriver/chromedriver"
        self.headless = True
        self.webdriver = None
        self.update_webdriver()

    def update_webdriver(self):
        opts = webdriver.ChromeOptions()
        opts.headless = self.headless
        driver_path = self.chromedriver_path
        driver = webdriver.Chrome(driver_path, options=opts)
        driver.set_page_load_timeout(self.browser_load_timeout)
        self.webdriver = driver

    def clean_domain(self, domain, type='normal'):
        """
        A method to clean up a domain so that we can load the page in our browser
        """

        # a list of things to remove from URL
        black_list = ["http:", "https:", "/", "www."]

        for item in black_list:
            domain = domain.replace(str(item), "")

        if type == 'webex':
            # Modify address for Webex Site
            domain = domain.replace(".", ".webex.")
            domain = f'http://{domain}'
        else:
            domain = f'http://www.{domain}'

        return domain

    def get_redirected_domain(self, domain):
        # Prepare response
        response = {
            'Website_Loaded': True,
            'All_Domains': [domain]
        }

        # Load a new webdriver
        self.update_webdriver()

        cleaned_domain = self.clean_domain(domain)
        resolved_cleaned_domain = None

        try:
            self.webdriver.get(cleaned_domain)

            # get the domain cleaned up for comparison
            resolved_domain = urlparse(self.webdriver.current_url).netloc
            resolved_cleaned_domain = self.clean_domain(resolved_domain)

        except TimeoutException:
             response['Website_Loaded'] = False

        # Close this loaded webdriver
        self.webdriver.close()

        if resolved_cleaned_domain is not None:
            if cleaned_domain == resolved_cleaned_domain:
                response['New_Domain_Found'] = False

            else:
                response['New_Domain_Found'] = True
                response['New_Domain'] = resolved_cleaned_domain
                response['All_Domains'] = [domain, resolved_cleaned_domain]

        return response






