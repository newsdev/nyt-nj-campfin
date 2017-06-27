import requests
from bs4 import BeautifulSoup
import time
import sys
import json
import re
import os

s = requests.session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Referer': 'http://www.elec.state.nj.us//ELECReport/SummaryData.aspx?Entity=tchL3XfmvD8%3d'

})
r = s.get('http://www.elec.state.nj.us//ELECReport/SummaryData.aspx?Entity=tchL3XfmvD8%3d')
soup = BeautifulSoup(r.text)
viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

data = {
    'ctl00$ContentPlaceHolder1$txtEntityId': '366087',
    'ctl00$ContentPlaceHolder1$rdoSelection': 'CD',
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

r = s.post('http://www.elec.state.nj.us//ELECReport/SummaryData.aspx?Entity=tchL3XfmvD8%3d', data=data)
if r.history:
    print "Request was redirected"
    for resp in r.history:
        print resp.status_code, resp.url
        print resp.headers
    print "Final destination:"
    print r.status_code, r.url
else:
    print "Request was not redirected"

print(r.headers)
print(r.content)