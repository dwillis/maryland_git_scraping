import csv
import requests
from bs4 import BeautifulSoup

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

if __name__ == "__main__":
    ola_reports()
