import sys
import json
import re
import os
import csv

import requests
import urllib.request
from bs4 import BeautifulSoup
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def get_json_file_from_url(url):
    data = []
    try:
        with urllib.request.urlopen(url) as json_file:
            data = json.loads(json_file.read().decode())
    except urllib.error.HTTPError:
        return []
    return data

def get_entity_data_from_url(entity_url, data_type_code):
    s = requests.session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cache-Control': 'max-age=0',
        'Referer': entity_url

    })
    r = s.get(entity_url)
    soup = BeautifulSoup(r.text)
    viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
    viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']
    txtEntityId = soup.find('input', {'name':'ctl00$ContentPlaceHolder1$txtEntityId'})['value']

    data = {
        'ctl00$ContentPlaceHolder1$txtEntityId': txtEntityId,
        'ctl00$ContentPlaceHolder1$rdoSelection': data_type_code,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl00': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl01': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl10': 'ltr',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl11': 'standards',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$AsyncWait$HiddenCancelField': 'False',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$collapse': 'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl05$ctl00$CurrentPage': '1',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl08$ClientClickedId': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$collapse': 'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$VisibilityState$ctl00': 'ReportPage',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ScrollPosition': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl02': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl03': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl04': '100',
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$BITSReportViewer1$btnDownloadData',
        '__EVENTARGUMENT': None,
        '__LASTFOCUS': None,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator
    }

    r = s.post(entity_url, data=data)
    return r.content

def get_campfin_data(url, data_type):
    entity_json = get_json_file_from_url(url)
    entity_urls = []
    data = []
    header = []

    for json_obj in entity_json:
        if json_obj['summary_link'] not in entity_urls:
            entity_url = json_obj['summary_link']
            entity_urls.append(json_obj['summary_link'])
            entity_data = get_entity_data_from_url(entity_url, data_type)
            print(entity_url)
            f = StringIO(entity_data.decode('utf-8'))

            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                row.append(json_obj['office_or_type'])
                row.append(json_obj['election_type'])
                row.append(json_obj['year'])
                data.append(row)
    
    header.extend(['office_or_type', 'election_type', 'year'])
    return (data, header)

def main():
    results = get_campfin_data(sys.argv[1], sys.argv[2])

    if (len(sys.argv) >= 3 and sys.argv[3] is not None and sys.argv[3] != ''):
        with open(sys.argv[3], 'w') as f:
            writer = csv.writer(f)
            writer.writerow(results[1])
            writer.writerows(results[0])
    else:
        print(results[0])

if __name__=='__main__':
    main()