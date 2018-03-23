from yapsy.IPlugin import IPlugin
import logging
import json
from urllib.request import urlopen

log = logging.getLogger('yapsy')

class RaiffeisenPlugin(IPlugin):
	def getRates(self):
		rates = []
		rates.append(-100) # No 1-year fixed

		json_data = json.load(urlopen('https://www.raiffeisen.ch/apiservices/www-mortgage-services/rest/products/1344'))
		for entry in json_data['products']['product']:
			if(entry['baseProperties']['model'] == 'FIXED'):
				# Found the fixed mortgages, now iterate the variants
				variants = entry['variants']['variant']
				for variant in variants:
					rate = variant['rate'][0]['interestRate']
					rates.append(rate)

				break;

		return rates