CREATE TABLE IF NOT EXISTS Customer(
  id INTEGER PRIMARY KEY, 
  email TEXT, 
  trialExpiration TEXT
);

CREATE TABLE IF NOT EXISTS Mortgage(
  id                  INTEGER PRIMARY KEY, 
  fk_customer         INTEGER,
  bank                TEXT,
  mortgageSum         REAL,
  liborMargin         REAL,
  discount            REAL,
  yearlyAmortization  REAL, 
  startDate           TEXT,
  paidInterest        REAL,
  FOREIGN KEY(fk_customer) REFERENCES Customer(id)
);

INSERT INTO Customer VALUES(NULL, "sebastian.hubrich@gmail.com", "2090-01-01");
INSERT INTO Mortgage VALUES(NULL, 1, "Raiffeisen", 540000, 0.9, 0.2, 1000, 2014-10-1, 0);