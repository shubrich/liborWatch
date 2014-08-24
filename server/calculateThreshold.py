# This Python file uses the following encoding: utf-8

import sqlite3
import datetime as dt
from datetime import datetime, timedelta
from calendar import monthrange


def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

def percentageOf(part, whole):
  return 100.0 * part/whole

def calculateThresholds():
	# Iterate the mortgage rows and calculate the threshold for each mortgage (the point where we'd have to switch to a fixed rate mortgage)
	today = dt.date.today().strftime('%Y-%m-%d')
	con = sqlite3.connect('liborWatch.sqlite')
	with con:
		cur = con.cursor()
		
		# Get the libor rates first
		cur.execute("SELECT * FROM LiborRate WHERE ID = (SELECT MAX(ID) FROM LiborRate)")
		liborResult = cur.fetchone()
		libor3Months = liborResult[2]
		libor6Months = liborResult[3]
		
		cur.execute("SELECT * FROM Mortgage")
		mortgageResults = cur.fetchall()
		for mortgage in mortgageResults:
			fixedRate = []
			cur.execute("SELECT * FROM BankRate WHERE bankName = ? AND date = ? ORDER BY fixedForYears", [mortgage[2], today])
			bankRateResults = cur.fetchall()
			
			for bankRate in bankRateResults:
				fixedRate.append(bankRate[4])

			mortgageID = mortgage[0]
			mortgageSum = mortgage[3]
			liborMargin = mortgage[4]
			yearlyAmortization = mortgage[6]
			interestPaid = mortgage[8]
			planningHorizon = mortgage[9] # Years
			maxInterestOverHorizon = mortgage[10] # Percent
			lastInterestPaidTS = mortgage[11]
			
			maxInterestCost = mortgageSum * planningHorizon * (maxInterestOverHorizon / 100)
			startDate = datetime.strptime(mortgage[7], '%Y-%m-%d')
			startDate = datetime.strptime('2014-01-25', '%Y-%m-%d')
			monthsSinceStartDate = monthdelta(startDate, dt.datetime.now())
			remainingMonthsInPlanningHorizon = ((planningHorizon * 12)) - monthsSinceStartDate
			residualDebt = mortgageSum - ((yearlyAmortization / 12) * monthsSinceStartDate)
			
			if lastInterestPaidTS is not None:
				lastInterestPaidTSDate = datetime.strptime(lastInterestPaidTS, '%Y-%m-%d')
				monthsSinceLastInterestPaidTS = monthdelta(lastInterestPaidTSDate, dt.datetime.now())
				if monthsSinceLastInterestPaidTS > 0:
					# TODO: Check if we have a 3 or 6 month libor
					newInterest = (residualDebt * ((libor3Months + liborMargin) / 100) / 12) * monthsSinceStartDate
					interestPaid += newInterest
					
					cur.execute("UPDATE Mortgage SET interestPaid=?, lastInterestPaidTS=? WHERE Id=?", (interestPaid, today, mortgageID))        
    				con.commit()
			else:
				if monthsSinceStartDate > 0:
					# TODO: Check if we have a 3 or 6 month libor
					newInterest = (residualDebt * ((libor3Months + liborMargin) / 100) / 12) * monthsSinceStartDate
					interestPaid += newInterest
					
					cur.execute("UPDATE Mortgage SET interestPaid=?, lastInterestPaidTS=? WHERE Id=?", (interestPaid, today, mortgageID))        
    				con.commit()
			
			lastMaxInterestResult = percentageOf((maxInterestCost - interestPaid) / (remainingMonthsInPlanningHorizon / 12.0), residualDebt)
			cur.execute("UPDATE Mortgage SET lastMaxInterestResult=? WHERE Id=?", (lastMaxInterestResult, mortgageID))        
			con.commit()
			
			# TODO: Implement a warning mechanism if lastMaxInterestResult is close (or over) to the interest rate
			# for a fixed mortgage that spans the remainingMonthsInPlanningHorizon
			
def main():   
	calculateThresholds()

if __name__ == "__main__":
    main()

