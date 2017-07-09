import requests
from bs4 import BeautifulSoup
import time
import sys
import json
import csv

def parse_contact_info(contact_html):
    splittable = contact_html.replace('</br>', '').replace('<br/>', '')
    fields = splittable.split('<br>')
    address = ''
    phone = ''
    fax = ''
    for field in fields:
        if 'Phone' in field:
            phone = field.split(':')[1].strip()
        elif 'Fax' in field:
            fax = field.split(':')[1].strip()
        else:
            address += field
            address += ' '

    return [address.strip(), phone.strip(), fax.strip()]

def get_aggregate_amount(amount_html):
    fields = amount_html.split('<br>')
    for field in fields:
        if 'Aggregate Amount' in field:
            return field.split('$')[1].strip()
    return ''

def get_property_contract_info():
    results = []

    s = requests.session()
    r = s.get('http://www.state.nj.us/treasury/dpmc/contract_search.shtml')
    soup = BeautifulSoup(r.text)

    discipline_menu = soup.find("select", {"name": "bydiscipline"})
    options = discipline_menu.find_all("option")
    values = [x.get('value') for x in options]

    s.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.state.nj.us',
        'Origin': 'http://www.state.nj.us',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cache-Control': 'max-age=0',
        'Referer': 'http://www.state.nj.us/treasury/dpmc/contract_search.shtml'
    })

    for value in values:
        if value == "":
            continue
        
        data = {
            "firmname": None,
            "bydiscipline": value,
            "bydiscipline1": None,
            "Start Search": "Start Search"
        }

        r = s.post("http://www.state.nj.us/cgi-bin/treas/contract_search.pl", data=data)
        soup = BeautifulSoup(r.text)
        rows = soup.find_all("tr", recursive=False)[:-1] #really hacky, but the html is apparently malformed and so this is what apparently gets the relevant rows

        for row in rows:
            contract = []
            contract.append(row.find("b").text)
            contract.extend(parse_contact_info(row.find("font", {"color": "#336633"}).decode_contents(formatter="html")))
            contract.append(get_aggregate_amount(row.find("font", color=lambda x: x != '#003399' and x != '#336633').decode_contents(formatter="html")))
            contract.append(row.find_all("font", color=lambda x: x == '#003399')[1].decode_contents(formatter="html"))
            results.append(contract)
    
    return results

def main():
    results = get_property_contract_info()
    if (len(sys.argv) >= 1 and sys.argv[1] is not None and sys.argv[1] != ''):
        with open(sys.argv[1], 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Vendor Name", "Vendor Address", "Vendor Phone", "Vendor Fax", "Aggregate Contract Amount", "Vendor Email"])
            writer.writerows(results)
    else:
        print(results)

if __name__=='__main__':
    main()