# This Python file uses the following encoding: utf-8

from yapsy.PluginManager import PluginManager
import requests
import sqlite3
import bs4
import datetime

def getLiborRates():
	response = requests.get("http://www.raiffeisen.ch/raiffeisen/internet/rb0027.nsf/webpagesbytitleall/965DD96752FF36F0C1256F2000248BA1")
	soup = bs4.BeautifulSoup(response.text)
	today = datetime.date.today().strftime('%d.%m.%Y')
	
	for table in soup.find_all('table'):
		if('vom: ' + today in table.tr.th.get_text()):
			td = table.find_all('td')
			if(len(td) >= 4):
				libor3Month = td[1].get_text()
				if(libor3Month.endswith('%')):
					libor3Month = libor3Month[:-2]
				
				libor6Month = td[3].get_text()
				if(libor6Month.endswith('%')):
					libor6Month = libor6Month[:-2]
				
				print('Libor 3 Monate = ' + libor3Month)
				print('Libor 6 Monate = ' + libor6Month)
			else:
				print('Error: Expected 4 entries in libor table but got ' + str(len(td)))
				
			newRate = []
			todayDB = datetime.datetime.strptime(today, '%d.%m.%Y').strftime('%Y-%m-%d')
			

			con = sqlite3.connect('liborWatch.sqlite')
			with con:
				cur = con.cursor()
				cur.execute("CREATE TABLE IF NOT EXISTS LiborRate(id INTEGER PRIMARY KEY, date TEXT, rate3Month REAL, rate6Month REAL)")
				cur.execute("INSERT INTO LiborRate VALUES(NULL, ?, ?, ?)", (todayDB, libor3Month, libor6Month))

def getBankRates():
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()

    # Loop round the plugins and print their names.
    for plugin in manager.getAllPlugins():
        plugin.plugin_object.print_name2()
			
def main():   
	getLiborRates()
	getBankRates()

if __name__ == "__main__":
    main()

