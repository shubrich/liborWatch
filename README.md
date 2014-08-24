liborWatch
==========

Monitor the CHF libor and calculate if it makes sense to switch over to a fixed mortgage.

Libor rates are better than fixed mortgage rates, but they fluctuate. If they rise we want to know when we have
to switch over to a fixed mortgage before we pay (a lot) more interest than we had if we had opted for a fixed mortgage 
from the beginning. So we have to monitor both libor and fixed rates to figure out when we have to switch over.

Define a timeframe and the maximum amount you are willing to spend over that timeframe for interest rates. 
Rule of thumb is to use a 10 year fixed mortgage rate from your bank and add 0.5%. Each year where the Libor rate
stays below the initial 10 year fixed rate we save money which adds to our buffer (and allows us to switch at a 
higher rate over to a fixed mortgage if we have to, before we lose money). 

The potential upside is that you can save money while the libor rate stays low.
The potential downside is that you lose money if the libor climbs.

liborWatch aims at keeping the risk low by telling you when best to switch over from libor to a fixed mortgage.

Example
-------
Let's assume a libor mortgage of 360k and a libor rate of 0.92%. If the libor rate doesn't change, this is how the
next years would look like if we only paid interest. Also assume a 10 year fixed rate of 2%. Let's add our buffer
of 0.5% and we have 2.5% over 10 years. This would result in paid interest of 90k over 10 years.

10-year cost = 360k * 2% * 10 years = 72'000  
10-year buffer cost = 360k * 2.5% * 10 years = 90'000  
10-year libor cost (assumption) = 360k * 0.92% * 10 years = 33'120  

Potential upside: 38'880 saved over 10 years
Potential downside: 18'000 spent more over 10 years if libor climbs

| Year | Mortgage  | Interest Paid | Remaining years | Max interest for mortgage over remaining years |
| -----|:---------:| -------------:| ----------------|:-----------------------------------------------|
| 0    | 360'000   |   3'312       |      10         |          2.316%                                |
| 1    | 360'000   |   6'624       |       9         |          2.573%                                |
| 2    | 360'000   |   9'936       |       8         |          2.780%                                |
| 3    | 360'000   |  13'248       |       7         |          3.046%                                |
| 4    | 360'000   |  16'560       |       6         |          3.400%                                |
| 5    | 360'000   |  19'872       |       5         |          3.896%                                |

How it works
============

Backend
-------
Scrape the banks website daily for the current fixed mortgage rate and save them in the database  
Scrape the banks website daily for the current libor rate and save them in the database  

TODO 
-----
Calculate daily all defined mortgages and notify if necessary  
API / Server (Express?, Sails? Django?, ...)  
UI to update values (Ember?, Backbone?)  




