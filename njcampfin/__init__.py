import requests
from bs4 import BeautifulSoup
import time
import sys
import json

def get_filing_list():
    #TODO make this take parameters, right now just does 2017 governor
    #with the exception of year, the fields have ids, so to do parameters
    #we have to put in a keyword-key conversion

    #this is candidate:list_of_filings
    results = {}

    #hit front page to get __EVENTVALIDATION and __VIEWSTATE
    s = requests.session()
    r = s.get('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx')
    soup = BeautifulSoup(r.text)
    viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'id':'__EVENTVALIDATION'})['value']

    #hit governor list page to get new fresh values of __EVENTVALIDATION and __VIEWSTATE
    #TODO will fail if there are more than 25, paginate.
    data = {"__EVENTTARGET":None,
        "__EVENTARGUMENT":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$Committee":"Candidate",
        "ctl00$ContentPlaceHolder1$usrSearch1$txtFirstName":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$txtMI":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$txtLastName":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$txtSuffix":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$ddlOffice":"0",
        "ctl00$ContentPlaceHolder1$usrSearch1$Location":"Location1",
        "ctl00$ContentPlaceHolder1$usrSearch1$ddlLocation1":None,
        "ctl00$ContentPlaceHolder1$usrSearch1$ddlParty":"ALL",
        "ctl00$ContentPlaceHolder1$usrSearch1$ddlElection":"ALL",
        "ctl00$ContentPlaceHolder1$usrSearch1$ddlYear":"2017",
        "ctl00$ContentPlaceHolder1$usrSearch1$btnSearch":"Search",
        '__VIEWSTATE':viewstate,
        '__EVENTVALIDATION':eventvalidation}
    r = s.post('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx', data=data)

    soup = BeautifulSoup(r.text)
    viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'id':'__EVENTVALIDATION'})['value']

    #hit links until we find one with no name, that means it's an error and we're done!
    i = 0
    while True:
        data = {'__EVENTTARGET':'ctl00$ContentPlaceHolder1$usrCommonGrid1$gvwData',
            '__EVENTARGUMENT':'Link${}'.format(i),
            '__LASTFOCUS':None,
            '__VIEWSTATE':viewstate,
            '__EVENTVALIDATION':eventvalidation,
            'ctl00$ContentPlaceHolder1$usrCommonGrid1$ddlRowsPerPage':'25'}

        r = s.post('http://www.elec.state.nj.us/ELECReport/SearchCandidate.aspx', data=data)
        soup = BeautifulSoup(r.text)
        i += 1
        name = soup.find('span', {'id':"ContentPlaceHolder1_usrCommonDetails1_lblName"})
        if name:
            name = name.text
            if name not in results:
                results[name] = []
            #find documents
            trs = soup.find('table', {'id': "ContentPlaceHolder1_usrCommonDetails1_usrCommonGrid1_gvwData"}).findAll('tr')
            for tr in trs:
                tds = tr.findAll('td')
                if len(tds) > 0:
                    details = {
                        'name' : name,
                        'date' : tds[0].text.strip(),
                        'form' : tds[1].text.strip(),
                        'period' : tds[2].text.strip(),
                        'amendment' : tds[3].text.strip(),
                        'doc_id' : tds[4].a['href'].split("=")[-1]}

                    results[name].append(details)
            
            time.sleep(1)
        else:
            break

    sys.stdout.write(json.dumps(results))
