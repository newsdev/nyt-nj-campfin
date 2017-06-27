from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
import sys
import time
import schedule
import os
import boto3
import urllib.request
from requests import get

bucket = os.environ['BUCKET_NAME']
folder = os.environ['FOLDER_PATH']
client = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)

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

def write_data(out, outfile):
    
    with open(outfile, 'w') as f:
        f.write(json.dumps(out))
    print("Results written")

    return out

def upload_json_to_s3(output_json, bucket, folder, filename):
    write_data(output_json, 'nj_campfin_scraped.json')
    client.upload_file('nj_campfin_scraped.json', bucket, folder + filename)

def get_previously_scraped_from_s3(output_filename):
    url = os.environ['AWS_URL_PREFIX'] + '/' + os.environ['BUCKET_NAME'] + '/' + os.environ['FOLDER_PATH'] + output_filename
    data = {}
    try:
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
    except urllib.error.HTTPError:
        return {}
    return data

def create_filing_name_from_json(filing_json):
    name = ''.join(x for x in filing_json['name'] if x.isalnum())
    date = ''.join(x for x in filing_json['date'] if x.isalnum())
    form = ''.join(x for x in filing_json['form'] if x.isalnum())

    out = name + date + form + '.pdf'
    return out

def get_filing_and_upload_to_s3(url, referer_url, bucket, folder, filename):
    reply = get(url, stream=True, headers={'Referer': referer_url})
    with open('temp_filing.pdf', 'wb') as file:
        for chunk in reply.iter_content(chunk_size=1024):
            if chunk:
                bytes = file.write(chunk)
    
    client.upload_file('temp_filing.pdf', bucket, folder+filename)
    file_url = os.environ['AWS_URL_PREFIX'] + '/' + os.environ['BUCKET_NAME'] + '/' + os.environ['FOLDER_PATH'] + filename
    return file_url

def get_filing_list(first_name, last_name, year, office, outfile):
    print("Began scraping with params {} {} {} {} {}".format(first_name, last_name, year, office, outfile))
    previously_scraped = []
    if outfile is not None and outfile != '':
        previously_scraped = get_previously_scraped_from_s3(outfile.split('/')[-1])

    #path_to_chromedriver = '/usr/local/bin/chromedriver' #TODO -> env var
    path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']
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
        wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
        wait.until(
            EC.presence_of_element_located((By.XPATH, docs_table_or_norecords_xpath))
        )

        names_table = browser.find_element_by_xpath(names_table_xpath)
        names_rows = names_table.find_elements_by_xpath("./tbody/tr")
        if check_exists_by_xpath("//a[text()='Summary Data']", browser):
            summary_data_link = browser.find_element_by_xpath("//a[text()='Summary Data']").get_attribute("href")
        else:
            summary_data_link = ''

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

            wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
            wait.until(
                EC.presence_of_element_located((By.XPATH, docs_table_or_norecords_xpath))
            )

            if (check_exists_by_xpath("//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09']//div[text()='No Records Found']", browser)):
                print("No records, continuing")
                continue

            browser.find_element_by_xpath(date_sort_controls_xpath).click()
            wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
            wait.until(EC.presence_of_element_located((By.XPATH, "//img[@src='/ELECReport/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=12.0.2402.20&Name=Microsoft.ReportingServices.Rendering.HtmlRenderer.RendererResources.sortAsc.gif']")))
            wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
            time.sleep(0.5)
            wait.until(
                EC.invisibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_AsyncWait"))
                #EC.element_to_be_clickable((By.XPATH, date_sort_controls_xpath))
            )
            browser.find_element_by_xpath(date_sort_controls_xpath).click()
            wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//img[@src='/ELECReport/Reserved.ReportViewerWebControl.axd?OpType=Resource&Version=12.0.2402.20&Name=Microsoft.ReportingServices.Rendering.HtmlRenderer.RendererResources.sortDesc.gif']"))
            )
            time.sleep(0.5)
            wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
            wait.until(
                EC.invisibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_AsyncWait"))
            )

            docs_table = browser.find_element_by_xpath(docs_table_xpath)
            filing_rows = docs_table.find_elements_by_xpath("./tbody/tr")
            for filing_row in filing_rows[2:]:
                filing_items = filing_row.find_elements_by_xpath(".//div")
                file_element = filing_row.find_element_by_xpath(".//a")
                details = {
                    'name': name.strip(),
                    'summary_link': summary_data_link
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
                
                
                if outfile is not None and outfile != '' and details not in previously_scraped:
                    details['url'] = ''
                    if details not in previously_scraped:
                        file_url = get_filing_and_upload_to_s3(file_element.get_attribute("href"), url, bucket, folder, create_filing_name_from_json(details))
                        print(file_url)
                        details['url'] = file_url
                else:
                    details['url'] = ''

                results.append(details)
        
        if check_exists_by_xpath(page_controls_xpath, browser):
            page_controls = browser.find_elements_by_xpath(page_controls_xpath)
        else:
            page_controls = None

        if page_controls == None or find_next_page_button_index(page_controls) == -1:
            break
        else:
            page_controls[find_next_page_button_index(page_controls)].click()
    
    if outfile is not None and outfile != '':
        write_data(results, outfile)
        upload_json_to_s3(results, bucket, folder, outfile.split('/')[-1])
    else:
        sys.stdout.write(json.dumps(results))

def main():
    get_filing_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    schedule.every(6).hours.do(get_filing_list, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__=='__main__':
    main()