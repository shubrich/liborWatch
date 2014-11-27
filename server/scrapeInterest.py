# This Python file uses the following encoding: utf-8

from yapsy.PluginManager import PluginManager
import requests
import sqlite3
import bs4
import datetime

def saveLiborRate(libor3Month, libor6Month):
	today = datetime.date.today().strftime('%d.%m.%Y')
	todayDB = datetime.datetime.strptime(today, '%d.%m.%Y').strftime('%Y-%m-%d')
	con = sqlite3.connect('liborWatch.sqlite')
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS LiborRate(id INTEGER PRIMARY KEY, date TEXT, rate3Month REAL, rate6Month REAL)")
		cur.execute("INSERT INTO LiborRate VALUES(NULL, ?, ?, ?)", (todayDB, libor3Month, libor6Month))

def getLiborRate(libor_url):
	response = requests.get(libor_url)
	soup = bs4.BeautifulSoup(response.text)

	tableCollection = soup.find_all('table')
	liborTable = tableCollection[1]
	liborTableRows = liborTable.find_all('tr')
	liborTableRowHeaders = liborTableRows[0].find_all('th')
	liborRate = liborTableRowHeaders[0].get_text()
	return liborRate

def getBankRates():
    # Load the plugins from the plugin directory.
	manager = PluginManager()
	manager.setPluginPlaces(["plugins"])
	manager.collectPlugins()
	today = datetime.date.today().strftime('%Y-%m-%d')

    # Loop round the plugins and get the bank rates
	for plugin in manager.getAllPlugins():
		rates = plugin.plugin_object.getRates()
		if(len(rates) != 10):
			print('Error: We did not get 10 rates from the plugin ' + plugin.name + ' - ' + str(len(rates)))
			return
			
		newRate = []
		iCnt = 0;
		for rate in rates:
			iCnt = iCnt + 1
			newRate.append((plugin.name, today, iCnt, rate))
			# print('execute insert statement ' + plugin.name, str(today), str(iCnt), str(rate))

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

