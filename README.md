# LinkedIn_Scraper
A few scripts to gather information from LinkedIn for prospecting of accounts for sales professionals

The script iterates through a list of accounts to check for several different things and provide information for prospecting a sales list

**Account list criteria**
 - The account list must be a .csv placed in the right folder
 - The account list must contain a list of account names - these are used for searching LinkedIn
 - The account list must also contain the company website for each account

**What does the scraper do**
 - 1. Checks Company Website
 - 2. Checks for presence of WebEx Website
 - 3. Checks for company on LinkedIn
 - 4. Saves all information in an output .csv with added columns

**1. Company Website Check**
 - Company websites are loaded in a web-browser and two different checks are made
   - Check to make sure the website loads. If the website doesn't load, the company may be out of business or having a hard time operating
   - Check to see if the website redirects.  If the website redirects, the company may have rebranded or been acquired

**2. Presence of WebEx Website**
 - For some salespeople, the presence of a WebEx Website is a useful indicator.  Especially if you are selling WebEx competitors.  WebEx has a specific convention using the company domain to host a webpage.  If this webpage exists, this is confirmation of a company being a current or former WebEx customer.
 - This script checks for the presence of this web page, and saves the result to the output .csv

**3. Presence of Company LinkedIn Page**
 - This is by far the most complex part of this script.  This component checks for a company on LinkedIn, cross references company websites to confirm, and if possible, gathers much of the company information stored on LinkedIn.  LinkedIn does not have a public facing API, so this script is built around using your personal LinedIn account to gather information.
 - The script has 3 key parts:
   - Login - Due to the way LinkedIn operates with Multi Factor Authentication, it is difficult to save a username and password in this script.  You instead will be prompted to log into LinkedIn on a visible web-page, which will likely require confirming receipt of a text message.  Then a cookie will be saved that can be used to use your LinkedIn account for the rest of the processes.
   - Search - This part uses the search feature of LinkedIn to find businesses with the same name.  Once found, it will navigate to the about page and gather some information.
   - Validation and Information gathering - Once a company's about page has been loaded, the company website in the provided account list is checked against the website listed on LinkedIn.  If these match, the script captures some information like the number of employees with LinkedIn accounts, the company's provided description, the general inducstry the company operates in, etc.

**4. Saving of List**
 - After every successful account is processed with the above 3 steps, the entire account list is saved with the updated information for the newly processed account.  You can periodically copy and past to get backups if you'd like.

**Performance**
 - This script is meant to be run on large lists, so it is not perfect.  It may fail on some accounts and this is fine.  It works a very high percentage of the time.
 - This script takes around 15 seconds per account to complete all 4 items above.  This leads to 250 accounts being processed per hour.
 - This script could EASILY be sped up or parallelized, however LinkedIn is not a fan of this type of script, so the intent is for it to process information at a somewhat reasonable rate to prevent having your LinkedIn account locked.

**Questions**
 - If you have any questions or need help troubleshooting, please don't hesitate to reach out.  This script has only been used by me as far as I know, so there will probably be a learning curve, but I would be happy to help.  I could also polish it up a bit to make it easier for others to use if needed.
