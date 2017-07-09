import sys
import json
import re
import os
import csv

import requests
import urllib.request
from bs4 import BeautifulSoup

contracts_url = 'http://www.nj.gov/treasury/purchase/noa/contracts/noa.shtml'

def extract_contract_info_from_page(html):
    contract_info = []
    soup = BeautifulSoup(html)
        
    vendor_table = soup.find('strong', text='VENDOR INFORMATION').findParents('table')[0]

    vendor_name_address_element = vendor_table.find(text='Vendor Name & Address:').findParents('tr')[0].find_all('td')[1]
    vendor_name_address_text = vendor_name_address_element.text.replace("\r", "").strip()
    vendor_name_address_components = re.split("\n+", vendor_name_address_text)
    contract_info.append(vendor_name_address_components[0])
    contract_info.append(' '.join(vendor_name_address_components[1:]))

    contact_person_element = vendor_table.find(text='Contact Person:').findParents('tr')[0].find_all('td')[1]
    contact_person_text = contact_person_element.text.replace("\r", "").strip()
    contract_info.append(contact_person_text)

    return contract_info

def get_contract_info():
    results = []
    failed_links = []

    s = requests.session()
    r = s.get(contracts_url)

    soup = BeautifulSoup(r.text)
    contracts_table = soup.find('table', {'bordercolor':'#003366'})
    contract_links = contracts_table.find_all('a')

    for link_element in contract_links:
        url = '/'.join(contracts_url.split('/')[:-1]) + '/' + link_element['href']
        if ('html' not in url):
            continue
        print(url)
        try:
            r = s.get(url)
            extracted_info = extract_contract_info_from_page(r.text)
            results.append(extracted_info)
        except ConnectionResetError:
            failed_links.append(url)
            print("Failed: " + url)

    while len(failed_links) > 0:
        print("Trying {} failed links again".format(len(failed_links)))
        url = failed_links.pop()
        try:
            r = s.get(url)
            extracted_info = extract_contract_info_from_page(r.text)
            results.append(extracted_info)
        except ConnectionResetError:
            failed_links.append(url)
            print("Failed: " + url)

    return results

def main():
    results = get_contract_info()
    if (len(sys.argv) >= 1 and sys.argv[1] is not None and sys.argv[1] != ''):
        with open(sys.argv[1], 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Vendor Name", "Vendor Address", "Contact Person"])
            writer.writerows(results)
    else:
        print(results)

if __name__=='__main__':
    main()