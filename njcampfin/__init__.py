from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
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
import csv

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
    data = []
    try:
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
    except urllib.error.HTTPError:
        return []
    return data

def create_filing_name_from_json(filing_json):
    name = ''.join(x for x in filing_json['name'] if x.isalnum())
    date = ''.join(x for x in filing_json['date'] if x.isalnum())
    form = ''.join(x for x in filing_json['form'] if x.isalnum())
    period = ''.join(x for x in filing_json['period'] if x.isalnum())
    amend = ''.join(x for x in filing_json['amend'] if x.isalnum())

    out = name + date + form + period + amend + '.pdf'
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

def advance_to_page(browser, page_controls_xpath, page_num):
    while True:
        if check_exists_by_xpath(page_controls_xpath, browser):
            page_controls = browser.find_elements_by_xpath(page_controls_xpath)
        else:
            page_controls = None
        advance_several = -1
        for i in range(len(page_controls)):
            if page_controls[i].text.strip() == str(page_num):
                page_controls[i].click()
                return
            elif page_controls[i].text == '>>':
                advance_several = i
        if advance_several == -1:
            raise ValueError("page_num out of range")
        else:
            page_controls[advance_several].click()

def convert_csv_row_to_result(csv_row):
    if len(csv_row) > 7:
        return {
            'name': csv_row[0],
            'summary_link': csv_row[1],
            'location': csv_row[2],
            'party': csv_row[3],
            'office_or_type': csv_row[4],
            'election_type': csv_row[5],
            'year': csv_row[6],
            'date': csv_row[7],
            'form': csv_row[8],
            'period': csv_row[9],
            'amendment': csv_row[10],
            'url': csv_row[11]
        }
    else:
        return {
            'name': csv_row[0],
            'summary_link': csv_row[1],
            'location': csv_row[2],
            'party': csv_row[3],
            'office_or_type': csv_row[4],
            'election_type': csv_row[5],
            'year': csv_row[6],
        }

def get_filing_list(first_name, last_name, year, office, outfile, get_filings, upload_pdfs, logfile):
    print("Began scraping with params {} {} {} {} {}".format(first_name, last_name, year, office, outfile))

    results = []
    if logfile is not None and logfile != '':
        reader = csv.reader(logfile)
        for row in reader:
            results.append(convert_csv_row_to_result(row))
        print(len(results))

    previously_scraped = []
    if outfile is not None and outfile != '':
        previously_scraped = get_previously_scraped_from_s3(outfile.split('/')[-1])

    previously_scraped_no_urls = []
    for old_details in previously_scraped:
        copy = dict(old_details)
        if 'url' in copy:
            del copy['url']
        previously_scraped_no_urls.append(copy)

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

    if len(results) > 25:
        advance_to_page(browser, page_controls_xpath, (len(results) // 25) + 1)
    if logfile is not None and logfile != '':
        writer = csv.writer(logfile)

    while True:
        wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
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

            try:
                name_row.click()
            except WebDriverException:
                print(" ".join([name, location, party, office_or_type, election_type, year]) + " FAILED")
                continue

            try:
                wait = WebDriverWait(browser, int(os.environ['WAIT_TIME']))
                wait.until(
                    EC.presence_of_element_located((By.XPATH, docs_table_or_norecords_xpath))
                )
            except TimeoutException:
                print("TIMEOUT EXCEPTION: " + name)

            if (check_exists_by_xpath("//div[@id='VisibleReportContentctl00_ContentPlaceHolder1_BITSReportViewer1_reportViewer1_ctl09']//div[text()='No Records Found']", browser)):
                print("No records, continuing")
                if get_filings:
                    continue

            if check_exists_by_xpath("//a[text()='Summary Data']", browser):
                summary_data_link = browser.find_element_by_xpath("//a[text()='Summary Data']").get_attribute("href")
            else:
                summary_data_link = ''

            if get_filings:
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
                        'summary_link': summary_data_link,
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
                        if details in previously_scraped_no_urls:
                            prev_details_index = previously_scraped_no_urls.index(details)
                            details['url'] = previously_scraped[prev_details_index]['url']
                        else:
                            details['url'] = ''
                        if details not in previously_scraped and upload_pdfs:
                            print("Downloading...")
                            file_url = get_filing_and_upload_to_s3(file_element.get_attribute("href"), url, bucket, folder, create_filing_name_from_json(details))
                            print(file_url)
                            details['url'] = file_url
                            pass
                    else:
                        details['url'] = ''
                    
                    if details not in results and logfile is not None and logfile != '':
                        writer.writerow([
                            details['name'],
                            details['summary_link'],
                            details['location'],
                            details['party'],
                            details['office_or_type'],
                            details['election_type'],
                            details['year'],
                            details['date'],
                            details['form'],
                            details['period'],
                            details['amendment'],
                            details['url']
                        ])
                        logfile.flush()
                    if details not in results:
                        results.append(details)
            else:
                details = {
                    'name': name.strip(),
                    'summary_link': summary_data_link,
                    'location': location,
                    'party': party,
                    'office_or_type': office_or_type,
                    'election_type': election_type,
                    'year': year,
                }

                if details not in results and logfile is not None and logfile != '':
                    writer.writerow([
                            details['name'],
                            details['summary_link'],
                            details['location'],
                            details['party'],
                            details['office_or_type'],
                            details['election_type'],
                            details['year'],
                    ])
                    logfile.flush()
                if details not in results:
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
    '''with open('log.csv', 'r+') as logfile:
    get_filing_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6].lower() == 'true', sys.argv[7].lower() == 'true', None)'''
    schedule.every(6).hours.do(get_filing_list, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[7].lower() == 'true', sys.argv[7].lower() == 'true', None)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__=='__main__':
    main()