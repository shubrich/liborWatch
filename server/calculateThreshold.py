# This Python file uses the following encoding: utf-8

import sqlite3
import smtplib
import datetime as dt
from datetime import datetime, timedelta
from calendar import monthrange
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def sendMail(recipient, subject, body):
	fromaddr = "liborWatch@nla-01.nextlevelapps.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = recipient
	msg['Subject'] = subject

	msg.attach(MIMEText(body, 'plain'))
	try:
		server = smtplib.SMTP('localhost')
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
	except:
		print("Exception while trying to send mail to {0}:\n\t{1}\n\t{2}".format(recipient, subject, body))
		return False


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
		
		cur.execute("SELECT Mortgage.id, Mortgage.fk_customer, Mortgage.bank, Mortgage.mortgageSum, Mortgage.liborMargin, Mortgage.discount, Mortgage.yearlyAmortization, Mortgage.startDate, Mortgage.interestPaid, Mortgage.planningHorizon, Mortgage.maxInterestOverHorizon, Mortgage.lastInterestPaidTS, Mortgage.lastMaxInterestResult, Mortgage.liborMonths, Customer.email FROM Mortgage INNER JOIN Customer ON Mortgage.fk_customer = Customer.id")
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
#			startDate = datetime.strptime('2014-01-25', '%Y-%m-%d')
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
			
			# Warning mechanism if lastMaxInterestResult is close (or over) to the interest rate
			# for a fixed mortgage that spans the remainingMonthsInPlanningHorizon
			fixedMortgageTime = remainingMonthsInPlanningHorizon / 12

			if (len(fixedRate) < fixedMortgageTime):
				subject = "liborWatch - ERROR"
				message = "There are only {0} fixed mortgage rates but we need {1}".format(len(fixedRate), fixedMortgageTime)
				sendMail(mortgage[14], subject, message)
				return
			
			matchingFixedRate = fixedRate[fixedMortgageTime - 1]
			if matchingFixedRate == -100:
				subject = "liborWatch - ERROR"
				message = "The matching fixed rate ({0} year(s)) doesn't seem to be available from this bank or we don't have rate information.".format(fixedMortgageTime)
				sendMail(mortgage[14], subject, message)
				return
			
			interestDifference = lastMaxInterestResult - matchingFixedRate
			if interestDifference > 0.5:
				return
			
			subject = "liborWatch"
			if interestDifference <= 0.5 and interestDifference > 0.3:
				subject = "liborWatch - INFO"
				
			
			if interestDifference <= 0.3 and interestDifference > 0.1:
				subject = "liborWatch - WARN"
			
			if interestDifference <= 0.1:
				subject = "liborWatch - WARN"

			message = "The rate for {0} years fixed mortgages ({1}%) approaches our threshold of {2}% with only {3}% difference".format(fixedMortgageTime, matchingFixedRate, lastMaxInterestResult, interestDifference)
			sendMail(mortgage[14], subject, message)

	
def main():   
	calculateThresholds()


if __name__ == "__main__":
    main()

