from yapsy.IPlugin import IPlugin
import logging
import requests
import bs4
import datetime

log = logging.getLogger('yapsy')

class RaiffeisenPlugin(IPlugin):
    def getRates(self):
		response = requests.get("http://www.raiffeisen.ch/raiffeisen/internet/rb0027.nsf/webpagesbytitleall/965DD96752FF36F0C1256F2000248BA1")
		soup = bs4.BeautifulSoup(response.text)
		today = datetime.date.today().strftime('%d.%m.%Y')
		rates = []
		rates.append(-100) # No 1-year fixed 
		
		for table in soup.find_all('table'):
			if('Festhypothek' in table.tr.th.get_text()):
				tdCollection = table.find_all('td')
				if(len(tdCollection) >= 18):
					iCnt = 1
					for td in tdCollection:
						if('Laufzeit' in td.get_text()):
							continue
						
						iCnt = iCnt + 1
						rate = td.get_text()
						if(rate.endswith('%')):
							rate = rate[:-2]
						rates.append(float(rate))
				else:
					print('Error: Expected 18 entries in mortgage table but got ' + str(len(tdCollection)))
					
		return rates


