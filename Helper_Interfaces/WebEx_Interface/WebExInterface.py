from Helper_Interfaces.Web_Interface.WebInterface import WebInterface
import selenium


class WebExInterface(WebInterface):

    def check_for_webex_site(self, domain_list):
        # create web driver
        self.update_webdriver()

        # set default values
        response = {
            'Checked_for_WebEx_Site': True,
        }

        # Filter to process account websites that exist
        for domain in domain_list:

            try:
                # Clean the domain before processing
                domain = self.clean_domain(domain, type='webex')
                print(f'Checking for webex site at : ', domain)

                # webex_check_url_from_salesforce = 'http://cdlschool.webex.com'
                # print(f"\nChecking if {account} has webex site set up ({webex_check_url_from_salesforce})")
                self.webdriver.get(domain)
                success = self.webdriver.find_element_by_class_name('join-input')
                if success:
                    response['WebEx_Site_Exists'] = True
                    response['WebEx_Domain'] = domain

            except selenium.common.exceptions.WebDriverException:
                pass

        return response
