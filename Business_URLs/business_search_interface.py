from selenium import webdriver
from urllib.parse import urlparse
import time
import us
import selenium


def get_company_linkedin_page(driver, company_name, company_url, state):
    print(f"\nStarted search for {company_name} in {state} with website {company_url}")
    # get a list of potential URLs for a company
    potential_urls = get_company_urls_from_search(driver, company_name)
    print("found these potential URLs from LinkedIn Search", potential_urls)
    num_search_results = len(potential_urls)

    # make sure URL is not nan, if not skip the url check
    check_url = True
    if company_url != company_url:
        # No url provided, so we don't want to check this
        print("no URL for this account")
        check_url = False

    for url in potential_urls:
        # navigate to company about page
        driver.get(f'{url}/about/')

        # wait on page to load
        time.sleep(0.5)

        if check_for_right_state(driver_at_about_page=driver, state=state):
            if not check_url:
                # we have the correct state and no URL on file
                print("Successfully found company in state (without URL check)", company_name, url, "-----------------")
                # Get all company information and return
                return num_search_results, url
            elif check_for_right_url(driver_at_about_page=driver, company_url=company_url):
                # We've found a business in the right state with the right URL
                print("Successfully found company, state, and URL", company_name, url, "-----------------------------")
                # Get all company information and return
                return num_search_results, url
            else:
                print("Found company in state, but URL didn't match", company_name, url)
        else:
            print("result not in right state - ", company_name, url)

    print("*** couldn't find ", company_name, " ***")

    return num_search_results, None


def get_company_details_from_linkedin(driver, company_linkedin_url):
    print(f"\nStarted details search for {company_linkedin_url}")

    # Create empty dict to add to
    company_details = {}

    # navigate to company about page and give time to load
    driver.get(f'{company_linkedin_url}/about/')
    time.sleep(1)

    company_details['LinkedIn Overview'] = driver.find_element_by_xpath("//*[contains(@id, 'ember')]/section/p").text

    title_list = []
    summary_titles = driver.find_elements_by_xpath("//*[contains(@id, 'ember')]/section/dl/dt")
    for i, item in enumerate(summary_titles):
        title_list.append(item.text)

    values_list = []
    summary_values = driver.find_elements_by_xpath("//*[contains(@id, 'ember')]/section/dl/dd")
    for i, item in enumerate(summary_values):
        values_list.append(item.text)

    offset = 0
    for i, title in enumerate(title_list):
        # company size needs to be handled differently since it might have 1 or 2 fields
        if title == "Company size":
            company_details['LinkedIn Company Size Range'] = values_list[i].split(" ")[0]
            if "LinkedIn" in values_list[i+1]:
                company_details["Employees on LinkedIn"] = values_list[i+1].split(" ")[0]
                offset = 1
        else:
            modified_title = f"LinkedIn {title}"
            company_details[modified_title] = values_list[i+offset]

    return company_details


def get_company_urls_from_search(driver, company_name, max_count=5):
    # Load Activity Calendar
    driver.get(f"https://www.linkedin.com/search/results/companies/?keywords={company_name}&origin=SWITCH_SEARCH_VERTICAL")

    # wait for the page to load
    time.sleep(0.5)

    # find all elements that have links
    elems = driver.find_elements_by_xpath("//a[@href]")

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


def check_for_right_state(driver_at_about_page, state):
    driver = driver_at_about_page

    # get abbreviations for state
    abbrev = us.states.lookup(state).abbr

    # Find location fields in the about page for the company
    potential_locations = driver.find_elements_by_class_name("org-top-card-summary-info-list__info-item")

    # Iterate through likely fields and check to see if the state name is in them
    for location in potential_locations:
        if state in location.text or abbrev in location.text:
            # we found a business with the same state, return the company information
            return True

    return False


def check_for_right_url(driver_at_about_page, company_url):

    driver = driver_at_about_page

    # Find location fields in the about page for the company
    potential_urls = driver.find_elements_by_xpath("//a[@href]")

    company_url_resolved_domain = get_resolved_domain(company_url)

    # iterate though all elements with links and add them to a list if they are a company link
    for linked_in_url in potential_urls:
        if "http://" in linked_in_url.text:
            if linked_in_url.text in company_url or company_url in linked_in_url.text:
                # there is a direct match with the company provided url and the LinkedIn URL
                return True
            elif company_url_resolved_domain == get_resolved_domain(linked_in_url.text):
                # there is a direct match with where both websites resolve
                return True

    return False


def get_resolved_domain(url):
    print("trying to resolve ", url)
    # Make a new web driver
    opts = webdriver.ChromeOptions()
    opts.headless = True
    new_driver = webdriver.Chrome('../login_tools/chromedriver', options=opts)
    new_driver.set_page_load_timeout(5)

    if "http" not in url:
        url = f'http://www.{url}'
    try:
        new_driver.get(url)
    except selenium.common.exceptions.TimeoutException:
        print('request timed out', url)
        return None
    time.sleep(1)

    # get the domain cleaned up for comparison
    resolved_domain = urlparse(new_driver.current_url).netloc
    resolved_domain = resolved_domain.replace("www.", "")

    print(f'url {url} resolved to {resolved_domain}')
    new_driver.close()

    return resolved_domain
