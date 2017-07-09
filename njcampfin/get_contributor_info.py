import sys
import json
import re
import os
import csv
import re

import requests
import urllib.request
from bs4 import BeautifulSoup
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from http.client import RemoteDisconnected
import errno
import traceback

url = 'http://elec.state.nj.us/ELECReport/searchcontributors.aspx'

def get_data_for_entity(entity):
    s = requests.session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cache-Control': 'max-age=0',
        'Referer': url

    })
    try:
        r = s.get(url)
    except Exception as e:
        print(traceback.format_exc())
        print(entity + " FAILED")
        return ''
    except OSError as e:
        if e.errno not in (errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE):
            raise
        else:
            print(entity + " FAILED")
            return ''
    except ConnectionResetError:
        print(entity + " FAILED")
        return ''
    except RemoteDisconnected:
        print(entity + " FAILED")
        return ''
    except requests.exceptions.ConnectionError:
        print(entity + " FAILED")
        return ''
    soup = BeautifulSoup(r.text)
    viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
    viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

    data = {
        '__EVENTTARGET': None,
        '__EVENTARGUMENT': None,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        'ctl00$ContentPlaceHolder1$txtContFirstName': None,
        'ctl00$ContentPlaceHolder1$txtContMI': None,
        'ctl00$ContentPlaceHolder1$txtContLastName': None,
        'ctl00$ContentPlaceHolder1$txtContSuffix': None,
        'ctl00$ContentPlaceHolder1$Ind:Committee': None,
        'ctl00$ContentPlaceHolder1$txtContCommitteeName': entity,
        'ctl00$ContentPlaceHolder1$txtStreet': None,
        'ctl00$ContentPlaceHolder1$txtCity': None,
        'ctl00$ContentPlaceHolder1$txtState': None,
        'ctl00$ContentPlaceHolder1$txtZip': None,
        'ctl00$ContentPlaceHolder1$txtStartDate': None,
        'ctl00$ContentPlaceHolder1$txtEndDate': None,
        'ctl00$ContentPlaceHolder1$txtStartAmount': None,
        'ctl00$ContentPlaceHolder1$txtEndAmount': None,
        'ctl00$ContentPlaceHolder1$ddlOccupation': 'ALL',
        'ctl00$ContentPlaceHolder1$txtEmployer': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$Committee':'Candidate',
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtFirstName': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtMI': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtLastName': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtSuffix': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$Location':'Location1',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlLocation1': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlOffice':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlParty':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlElection':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlYear':'ALL',
        'ctl00$ContentPlaceHolder1$btnSearch':'Search',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl00': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl01': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl10': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl11':'standards',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$AsyncWait$HiddenCancelField':'False',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$collapse':'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl08$ClientClickedId': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$collapse':'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$VisibilityState$ctl00':'None',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ScrollPosition': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl02': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl03': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl04':'100'
    }

    try:
        r = s.post(url, data=data)
    except Exception as e:
        print(traceback.format_exc())
        print(entity + " FAILED")
        return ''
    except OSError as e:
        if e.errno not in (errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE):
            raise
        else:
            print(entity + " FAILED")
            return ''
    except ConnectionResetError:
        print(entity + " FAILED")
        return ''
    except RemoteDisconnected:
        print(entity + " FAILED")
        return ''
    except requests.exceptions.ConnectionError:
        print(entity + " FAILED")
        return ''
    soup = BeautifulSoup(r.text)

    if soup.find('input', {'id':'__VIEWSTATE'}) is None:
        print(entity + " FAILED")
        return ''
    viewstate = soup.find('input', {'id':'__VIEWSTATE'})['value']
    viewstategenerator = soup.find('input', {'id':'__VIEWSTATEGENERATOR'})['value']

    data = {
        'ctl00$ContentPlaceHolder1$txtContFirstName': None,
        'ctl00$ContentPlaceHolder1$txtContMI': None,
        'ctl00$ContentPlaceHolder1$txtContLastName': None,
        'ctl00$ContentPlaceHolder1$txtContSuffix': None,
        'ctl00$ContentPlaceHolder1$Ind': 'Committee',
        'ctl00$ContentPlaceHolder1$txtContCommitteeName': entity,
        'ctl00$ContentPlaceHolder1$txtStreet': None,
        'ctl00$ContentPlaceHolder1$txtCity': None,
        'ctl00$ContentPlaceHolder1$txtState': None,
        'ctl00$ContentPlaceHolder1$txtZip': None,
        'ctl00$ContentPlaceHolder1$txtStartDate': None,
        'ctl00$ContentPlaceHolder1$txtEndDate': None,
        'ctl00$ContentPlaceHolder1$txtStartAmount': None,
        'ctl00$ContentPlaceHolder1$txtEndAmount': None,
        'ctl00$ContentPlaceHolder1$ddlOccupation': 'ALL',
        'ctl00$ContentPlaceHolder1$txtEmployer': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$Committee':'Candidate',
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtFirstName': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtMI': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtLastName': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$txtSuffix': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$Location':'Location1',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlLocation1': None,
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlOffice':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlParty':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlElection':'ALL',
        'ctl00$ContentPlaceHolder1$usrCandidate1$ddlYear':'ALL',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl00': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl03$ctl01': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl10':'ltr',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl11':'standards',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$AsyncWait$HiddenCancelField':'False',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ToggleParam$collapse':'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl05$ctl00$CurrentPage':'1',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl08$ClientClickedId': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$store': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl07$collapse':'false',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$VisibilityState$ctl00':'ReportPage',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ScrollPosition': None,
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl02':'',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl03':'',
        'ctl00$ContentPlaceHolder1$BITSReportViewer1$reportViewer1$ctl09$ReportControl$ctl04':'100',
        '__EVENTTARGET':'ctl00$ContentPlaceHolder1$BITSReportViewer1$btnDownloadData',
        '__EVENTARGUMENT': None,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator
    }

    try:
        r = s.post(url, data=data)
    except Exception as e:
        print(traceback.format_exc())
        print(entity + " FAILED")
        return ''
    except OSError as e:
        if e.errno not in (errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE):
            raise
        else:
            print(entity + " FAILED")
            return ''
    except ConnectionResetError:
        print(entity + " FAILED")
        return ''
    except RemoteDisconnected:
        print(entity + " FAILED")
        return ''
    except requests.exceptions.ConnectionError:
        print(entity + " FAILED")
        return ''
    return r.content

def clean_organization_name(name):
    pattern = re.compile(r"[^a-zA-Z '-]+")
    copattern = re.compile(r"\bco\b")
    incpattern = re.compile(r"\binc\b")
    llcpattern = re.compile(r"\bllc\b")
    alphanum = pattern.sub('', name).lower()
    noco = copattern.sub('', alphanum)
    noinc = incpattern.sub('', noco)
    nollc = llcpattern.sub('', noinc)
    return nollc

def main():
    entities = []
    header = []
    results = []
    with open(sys.argv[1], 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            entities.append(clean_organization_name(row[0]))
    for entity in entities:
        entity_data = get_data_for_entity(entity)
        if entity_data == '':
            continue
        f = StringIO(entity_data.decode('utf-8'))
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            results.append(row)
        print(entity)

    if (len(sys.argv) >= 2 and sys.argv[2] is not None and sys.argv[2] != ''):
        with open(sys.argv[2], 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(results)
    else:
        print(results)


if __name__=='__main__':
    main()