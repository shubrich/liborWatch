# This Python file uses the following encoding: utf-8

from yapsy.PluginManager import PluginManager
import requests
import sqlite3
import bs4
import datetime
import logging
logging.basicConfig()
log = logging.getLogger('yapsy')

def saveLiborRate(libor3Month, libor6Month):
	today = datetime.date.today().strftime('%d.%m.%Y')
	todayDB = datetime.datetime.strptime(today, '%d.%m.%Y').strftime('%Y-%m-%d')
	con = sqlite3.connect('liborWatch.sqlite')
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS LiborRate(id INTEGER PRIMARY KEY, date TEXT, rate3Month REAL, rate6Month REAL)")
		cur.execute("INSERT INTO LiborRate VALUES(NULL, ?, ?, ?)", (todayDB, libor3Month, libor6Month))

def getLiborRate(libor_url):
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36'
		}

	response = requests.get(libor_url, headers=headers)
	soup = bs4.BeautifulSoup(response.text, "html.parser")

	tableCollection = soup.find_all('table')
	liborTable = tableCollection[1]
	liborTableRows = liborTable.find_all('tr')
	liborTableRowData = liborTableRows[1].find_all('td')
	liborRate = liborTableRowData[1].get_text()
	return liborRate

def getBankRates():
    # Load the plugins from the plugin directory.
	manager = PluginManager()
	# Server
	# manager.setPluginPlaces(["./dev/liborWatch/server/plugins"])
	# Dev
	# manager.setPluginPlaces(["./plugins"])
	# Local
	manager.setPluginPlaces(["./dev/NextLevelApps/liborWatch/server/plugins"])

	manager.collectPlugins()
	today = datetime.date.today().strftime('%Y-%m-%d')

    # Loop round the plugins and get the bank rates
	for plugin in manager.getAllPlugins():
		rates = plugin.plugin_object.getRates()
		print(rates);
		if(len(rates) != 10):
			print('Error: We did not get 10 rates from the plugin ' + plugin.name + ' - ' + str(len(rates)))
			return

		newRate = []
		iCnt = 0;
		for rate in rates:
			iCnt = iCnt + 1
			newRate.append((plugin.name, today, iCnt, rate))
#			print('execute insert statement ' + plugin.name, str(today), str(iCnt), str(rate))

		con = sqlite3.connect('liborWatch.sqlite')
		with con:
			cur = con.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS BankRate(id INTEGER PRIMARY KEY, bankName TEXT, date TEXT, fixedForYears INTEGER, rate REAL)")
			cur.executemany("INSERT INTO BankRate VALUES(NULL, ?, ?, ?, ?)", newRate)



def main():
	libor3Months = getLiborRate("http://www.finanzen.ch/zinsen/Libor-CHF-3-Monate")
	libor6Months = getLiborRate("http://www.finanzen.ch/zinsen/Libor-CHF-6-Monate")
	saveLiborRate(libor3Months, libor6Months)
	getBankRates()

if __name__ == "__main__":
    main()

