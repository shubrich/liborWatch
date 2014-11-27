import requests
import sqlite3
import bs4
import datetime

# response = requests.get("http://www.finanzen.ch/zinsen/Libor-CHF-3-Monate")
response = requests.get("http://www.finanzen.ch/zinsen/Libor-CHF-6-Monate")
soup = bs4.BeautifulSoup(response.text)
today = datetime.date.today().strftime('%d.%m.%Y')
libor3Month = 0
libor6Month = 0
found3MonthLibor = False
found6MonthLibor = False

tableCollection = soup.find_all('table')
liborTable = tableCollection[1]
liborTableRows = liborTable.find_all('tr')
liborTableRowHeaders = liborTableRows[0].find_all('th')
liborRate = liborTableRowHeaders[0].get_text()

print("liborRate = " + str(liborRate))

    
# todayDB = datetime.datetime.strptime(today, '%d.%m.%Y').strftime('%Y-%m-%d')
# print("libor3Month = " + str(libor3Month))
# print("libor6Month = " + str(libor6Month))