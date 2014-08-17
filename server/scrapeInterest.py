from yapsy.PluginManager import PluginManager
import feedparser
import datetime
import sqlite3

def getLibor():
	# Get 3-month CHF Libor
	
	# Get 6-month CHF Libor
	
	d=feedparser.parse("http://www.snb.ch/selector/en/mmr/intfeed/rss")
#	today = datetime.date.today()
	today = datetime.date(2014,8,14)
	print(str(today))
	for post in d.entries:
		if "LIB " + str(today) in post.title:
			print post.title + ": " + post.link + "\n"
			print post["cb_value"]
			
			newRate = []
			newRate.append((post["cb_value"], today))

			con = sqlite3.connect('liborWatch.sqlite')
			with con:
				cur = con.cursor()
				cur.execute("CREATE TABLE IF NOT EXISTS Rates(id INTEGER PRIMARY KEY, date TEXT, rate REAL)")
				cur.executemany("INSERT INTO Rates VALUES(NULL, ?, ?)", newRate)
			
			# Look for today's title post:
			# 'title': u'CH: 0.02 LIB 2014-08-14 SNB 3-month LIBOR CHF'
		
			
def main():   
#    # Load the plugins from the plugin directory.
#    manager = PluginManager()
#    manager.setPluginPlaces(["plugins"])
#    manager.collectPlugins()
#
#    # Loop round the plugins and print their names.
#    for plugin in manager.getAllPlugins():
#        plugin.plugin_object.print_name2()
	getLibor()

if __name__ == "__main__":
    main()

