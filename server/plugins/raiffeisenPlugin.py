from yapsy.IPlugin import IPlugin
import logging
import bs4
import dryscrape

log = logging.getLogger('yapsy')

class RaiffeisenPlugin(IPlugin):
	def getRates(self):
		my_url = "https://www.raiffeisen.ch/schaffhausen/de/privatkunden/hypotheken/hypopedia/finanzieren/hypothekenzinsen.html"

		session = dryscrape.Session()
		session.visit(my_url)
		response = session.body()
		soup = bs4.BeautifulSoup(response)
		rates = []
		rates.append(-100) # No 1-year fixed 

		for table in soup.find_all('table'):
			if table.tr.th is None:
				continue

			if('Festhypothek' in table.tr.th.get_text()):
				tdCollection = table.find_all('td')

				if(len(tdCollection) >= 18):
					iCnt = 1
					for td in tdCollection:
						if('Jahre' in td.get_text()):
							continue

					iCnt = iCnt + 1

					# Get the rates for "1. Hypothek"
					if iCnt % 2 == 1:
					  continue

					rate = td.get_text()
					if(rate.endswith('%')):
						rate = rate[:-2]
						rates.append(float(rate))
				else:
					print('Error: Expected 18 entries in mortgage table but got ' + str(len(tdCollection)))

		return rates


