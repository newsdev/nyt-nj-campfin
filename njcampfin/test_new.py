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
    'Cookie': 'ASP.NET_SessionId=2w4r4q25gvy03j2vxuejt2u4'
})
r = s.get('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx')
soup = BeautifulSoup(r.text)
viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

data = {
    "__EVENTTARGET":None,
    "__EVENTARGUMENT":None,
    "ctl00$ContentPlaceHolder1$usrCandidate1$Committee":"Candidate",
    "ctl00$ContentPlaceHolder1$usrCandidate1$txtFirstName":"Phil",
    "ctl00$ContentPlaceHolder1$usrCandidate1$txtMI":None,
    "ctl00$ContentPlaceHolder1$usrCandidate1$txtLastName":"Murphy",
    "ctl00$ContentPlaceHolder1$usrCandidate1$txtSuffix":None,
    "ctl00$ContentPlaceHolder1$usrCandidate1$ddlOffice":"ALL",
    "ctl00$ContentPlaceHolder1$usrCandidate1$Location":"Location1",
    "ctl00$ContentPlaceHolder1$usrCandidate1$ddlLocation1":None,
    "ctl00$ContentPlaceHolder1$usrCandidate1$ddlParty":"ALL",
    "ctl00$ContentPlaceHolder1$usrCandidate1$ddlElection":"ALL",
    "ctl00$ContentPlaceHolder1$usrCandidate1$ddlYear":"2017",
    "ctl00$ContentPlaceHolder1$usrCandidate1$btnSearch":"Search",
    '__VIEWSTATE':viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator
}

r = s.post('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx', data=data)
soup = BeautifulSoup(r.text)

path = os.path.abspath('temp.html')
url = 'file://' + path

with open(path, 'w') as f:
    f.write(r.text)

viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

data2 = {
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl03': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl02': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$collapse': 'false', 
    '__EVENTARGUMENT': 'Link$1', 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$VisibilityState$ctl00': 
    'ReportPage', 
    '__VIEWSTATEGENERATOR': viewstategenerator,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$collapse': 'false', 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$store': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl04': '100',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl08$ClientClickedId': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ScrollPosition': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl05$ctl00$CurrentPage': '1',
    '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$usrCommonGrid1$gvwData',
    '__VIEWSTATE': viewstate,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl11':'standards',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl10': 'ltr',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$AsyncWait$HiddenCancelField': 'False',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl00': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl01': None
}

r = s.post('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx', data=data2)
soup = BeautifulSoup(r.text)
results = soup.findAll('table')
for elem in soup(text=re.compile(r'Date Recieved')):
    print(elem.parent)

path = os.path.abspath('temp2.html')
url = 'file://' + path

with open(path, 'w') as f:
    f.write(r.text)

viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

data3 = {
    'ctl00$ScriptManager1': 'ctl00$ScriptManager1|ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$Reserved_AsyncLoadTarget',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl00': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl01': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl05$ctl00$CurrentPage': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl03': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl02': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$collapse': 'false', 
    '__EVENTARGUMENT': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$VisibilityState$ctl00': 'None', 
    '__VIEWSTATEGENERATOR': viewstategenerator,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$collapse': 'false', 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$store': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl04': '100',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl08$ClientClickedId': None, 
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ScrollPosition': None,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl05$ctl00$CurrentPage': None,
    '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$Reserved_AsyncLoadTarget',
    '__VIEWSTATE': viewstate,
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl11':'standards',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl10': 'ltr',
    'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$AsyncWait$HiddenCancelField': 'False',
    '__ASYNCPOST': 'true'
}


s.headers.update({
    'X-MicrosoftAjax': 'Delta=true',
    'X-Requested-With': 'XMLHttpRequest'
})

r = s.post('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx', data=data3)
soup = BeautifulSoup(r.text)
results = soup.findAll('table')
for elem in soup(text=re.compile(r'Date Recieved')):
    print(elem.parent)

path = os.path.abspath('temp3.html')
url = 'file://' + path

with open(path, 'w') as f:
    f.write(r.text)
