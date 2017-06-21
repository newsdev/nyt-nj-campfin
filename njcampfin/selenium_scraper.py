from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import sys

path_to_chromedriver = '/Users/208301/chromedriver2' #TODO -> env var
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

url = 'http://www.elec.state.nj.us/ELECReport/searchcandidate.aspx' #TODO -> env var, maybe?

browser.get(url)

browser.find_element_by_id('txtFirstName').send_keys("Phil")
browser.find_element_by_id('txtLastName').send_keys("Murphy")

browser.find_element_by_id('btnSearch').click()

docs_table_xpath = "//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09']//table[@cols='6']"
names_table_xpath = "//table[@id='ContentPlaceHolder1_usrCommonGrid1_gvwData']"
names_page_links_template = "ContentPlaceHolder1_usrCommonGrid1_rptPaging_LinkButton1_{}"

wait = WebDriverWait(browser, 10)
wait.until(
    EC.presence_of_element_located((By.XPATH, docs_table_xpath))
)

names_table = browser.find_element_by_xpath(names_table_xpath)
names_rows = names_table.find_elements_by_xpath("./tbody/tr")
results = []

for i in range(1, len(names_rows)):
    names_table = browser.find_element_by_xpath(names_table_xpath)
    names_rows = names_table.find_elements_by_xpath("./tbody/tr")
    name_row = names_rows[i]

    name = name_row.find_element_by_xpath("./td/a").text
    name_items = name_row.find_elements_by_xpath("./td")
    location = name_items[1].text
    party = name_items[2].text
    office_or_type = name_items[3].text
    election_type = name_items[4].text
    year = name_items[5].text
    name_row.click()

    wait = WebDriverWait(browser, 10)
    wait.until(
        EC.presence_of_element_located((By.XPATH, docs_table_xpath))
    )

    docs_table = browser.find_element_by_xpath(docs_table_xpath)
    filing_rows = docs_table.find_elements_by_xpath("./tbody/tr")
    for filing_row in filing_rows[2:]:
        filing_items = filing_row.find_elements_by_xpath(".//div")
        file_element = filing_row.find_elements_by_xpath(".//a")
        details = {
            'name': name.strip(),
            'location': location,
            'party': party,
            'office_or_type': office_or_type,
            'election_type': election_type,
            'year': year,
            'date': filing_items[0].text.strip(),
            'form': filing_items[1].text.strip(),
            'period': filing_items[2].text.strip(),
            'amendment' : filing_items[3].text.strip(),
        }

        results.append(details)

sys.stdout.write(json.dumps(results))
