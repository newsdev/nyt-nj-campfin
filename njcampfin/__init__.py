from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
import sys
import time

def check_exists_by_id(id, driver):
    try:
        driver.find_element_by_id(id)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def find_next_page_button_index(elements):
    for i in range(len(elements)):
        if elements[i].text == ' > ':
            return i
    return -1

def get_filing_list(first_name, last_name, year, office):
    path_to_chromedriver = '/usr/local/bin/chromedriver' #TODO -> env var
    browser = webdriver.Chrome(executable_path = path_to_chromedriver)

    url = 'http://www.elec.state.nj.us/ELECReport/searchcandidate.aspx' #TODO -> env var, maybe?

    browser.get(url)

    browser.find_element_by_id('txtFirstName').send_keys(first_name)
    browser.find_element_by_id('txtLastName').send_keys(last_name)
    if (year is not None and year != ''):
        browser.find_element_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$usrCandidate1$ddlYear']/option[text()='{}']".format(year)).click()
    if (office is not None and office != ''):
        browser.find_element_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$usrCandidate1$ddlOffice']/option[text()='{}']".format(office)).click()

    browser.find_element_by_id('btnSearch').click()

    docs_table_xpath =  "//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09']//table[@cols='6']"
    docs_table_or_norecords_xpath = "//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09'][.//table[@cols='6'] or .//div/text()='No Records Found']"
    names_table_xpath = "//table[@id='ContentPlaceHolder1_usrCommonGrid1_gvwData']"
    names_page_links_template = "ContentPlaceHolder1_usrCommonGrid1_rptPaging_LinkButton1_{}"
    page_controls_xpath = "//a[@class='bodytext']"
    date_sort_controls_xpath = "//td/a[@tabindex]"

    if check_exists_by_xpath(page_controls_xpath, browser):
        page_controls = browser.find_elements_by_xpath(page_controls_xpath)
    else:
        page_controls = None

    results = []
    while True:
        wait = WebDriverWait(browser, 300)
        wait.until(
            EC.presence_of_element_located((By.XPATH, docs_table_or_norecords_xpath))
        )

        names_table = browser.find_element_by_xpath(names_table_xpath)
        names_rows = names_table.find_elements_by_xpath("./tbody/tr")

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

            wait = WebDriverWait(browser, 300)
            wait.until(
                EC.presence_of_element_located((By.XPATH, docs_table_or_norecords_xpath))
            )

            if (check_exists_by_xpath("//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09']//div[text()='No Records Found']", browser)):
                print("No records, continuing")
                continue

            browser.find_element_by_xpath(date_sort_controls_xpath).click()
            wait = WebDriverWait(browser, 300)
            wait.until(EC.presence_of_element_located((By.XPATH, "//img[@src='/ELECReport/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=12.0.2402.20&Name=Microsoft.ReportingServices.Rendering.HtmlRenderer.RendererResources.sortAsc.gif']")))
            wait = WebDriverWait(browser, 300)
            time.sleep(0.5)
            wait.until(
                EC.invisibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_AsyncWait"))
                #EC.element_to_be_clickable((By.XPATH, date_sort_controls_xpath))
            )
            browser.find_element_by_xpath(date_sort_controls_xpath).click()
            wait = WebDriverWait(browser, 300)
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//img[@src='/ELECReport/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=12.0.2402.20&Name=Microsoft.ReportingServices.Rendering.HtmlRenderer.RendererResources.sortDesc.gif']"))
            )
            time.sleep(0.5)
            wait = WebDriverWait(browser, 300)
            wait.until(
                EC.invisibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_AsyncWait"))
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
        
        if check_exists_by_xpath(page_controls_xpath, browser):
            page_controls = browser.find_elements_by_xpath(page_controls_xpath)
        else:
            page_controls = None

        if page_controls == None or find_next_page_button_index(page_controls) == -1:
            break
        else:
            page_controls[find_next_page_button_index(page_controls)].click()

    sys.stdout.write(json.dumps(results))

def main():
    get_filing_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__=='__main__':
    main()