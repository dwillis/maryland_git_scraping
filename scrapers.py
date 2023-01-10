import csv
import datetime
import itertools
import requests
from bs4 import BeautifulSoup

def absentee_ballots():
    today = datetime.date.today()
    date_string = today.strftime("%Y%m%d")
    url = "https://elections.maryland.gov/press_room/2022_stats/GG22/Absentees%20Sent%20and%20Returned%20by%20County.xlsx"
    response = requests.get(url)
    with open(f"absentee/absentee_ballots_{date_string}.xlsx", 'wb') as output_file:
        output_file.write(response.content)

def ola_reports():
    url = 'https://www.ola.state.md.us/Search/Report?keyword=&agencyId=&dateFrom=&dateTo='
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find('tbody')
    list_of_rows = []
    for row in table.find_all('tr'):
        list_of_cells = []
        for cell in row.find_all('td'):
            if cell.find('a'):
                list_of_cells.append("https://www.ola.state.md.us" + cell.find('a')['href'])
            text = cell.text.strip()
            list_of_cells.append(text)
        list_of_rows.append(list_of_cells)

    outfile = open("ola_reports.csv", "w")
    writer = csv.writer(outfile)
    writer.writerow(["date", "type", "url", "title"])
    writer.writerows(list_of_rows)

def phonebook():
    today = datetime.date.today()
    date_string = today.strftime("%Y%m%d")
    # get agencies
    agency_urls = []
    url = "https://www.doit.state.md.us/phonebook/orglisting.asp"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content
    soup = BeautifulSoup(html, features="html.parser")
    tables = soup.find_all('tbody')
    for table in tables:
        agency_urls.append(["https://www.doit.state.md.us/phonebook/"+x.find('a')['href'] for x in table.find_all('td')])
    flattened_urls = itertools.chain(*agency_urls)
    final_agency_urls = list(flattened_urls)

    # get subagency urls:
    subagency_urls = []
    for agency_url in final_agency_urls:
        response = requests.get(agency_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.content
        soup = BeautifulSoup(html, features="html.parser")
        tables = soup.find_all('tbody')
        for table in tables:
            subagency_urls.append(["https://www.doit.state.md.us/phonebook/"+x['href'] for x in table.find_all('a')])
        flattened_subagency_urls = itertools.chain(*subagency_urls)
        final_subagency_urls = list(flattened_subagency_urls)

    # get listings from each subagency
    urls = []
    listings = []
    for subagency_url in final_subagency_urls:
        oid = subagency_url.split('=')[1]
        response = requests.get(subagency_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.content
        soup = BeautifulSoup(html, features="html.parser")
        agency = soup.find('h1').text.strip()
        subagency = soup.find_all('h2')[2].text.strip()
        if subagency == 'General Information':
            continue
        tables = soup.find_all('tbody')
        for table in tables:
            for row in table.find_all('tr'):
                if row.find_all('td')[1].text.strip().upper() in ['GENERAL LISTING', 'TTY', 'TOLL FREE', 'MARYLAND TOLL FREE', 'GENERAL ASSISTANCE', 'FAX NUMBER', 'INFORMATION', 'TOLL FREE NUMBER', 'FACSIMILE', 'FACSIMILE NUMBER', 'FASCIMILE NUMBER', 'MAIN NUMBERS', 'MAIN NUMBER', 'GENERAL INFORMATION', 'GENERAL ASSEMBLY INFORMATION']:
                    continue
                if row.find_all('td')[1].text.strip() == '':
                    continue
                if row.find_all('td')[2].text.strip().upper() in ['TTY', 'FAX NUMBER', 'FACSIMILE', 'MARYLAND TOLL FREE', 'GENERAL ASSISTANCE', 'FACSIMILE NUMBER', 'INFORMATION', 'TOLL FREE', 'TOLL FREE NUMBER', 'GENERAL INFORMATION', 'MAIN NUMBER', 'MAIN OFFICE NUMBER', 'EMERGENCY RESPONSE', 'INFORMATION:', 'INFORMATION TECHNOLOGY DIVISION', 'HISPANIC INFORMATION']:
                    continue
                record = []
                record.append(oid)
                record.append(agency)
                record.append(subagency)
                for cell in row.find_all('td'):
                    if cell.find('a'):
                        if cell.find('a')['href'] not in urls:
                            url = "https://www.doit.state.md.us/phonebook/"+cell.find('a')['href']
                            record.append(url)
                            record.append(cell.text.strip())
                            urls.append(url)
                    else:
                        record.append(cell.text.strip())
                listings.append(record)
    with open(f"directory/directory_{date_string}.csv", "w") as output_file:
        csvfile = csv.writer(output_file)
        csvfile.writerow(['oid', 'agency', 'office', 'url', 'name', 'title', 'phone'])
        csvfile.writerows(listings)

if __name__ == "__main__":
    ola_reports()
    phonebook()
