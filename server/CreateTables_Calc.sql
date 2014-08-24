DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Mortgage;

CREATE TABLE Customer(
  id INTEGER PRIMARY KEY, 
  email TEXT, 
  trialExpiration TEXT
);

CREATE TABLE Mortgage(
  id                      INTEGER PRIMARY KEY, 
  fk_customer             INTEGER,  -- ID des Kunden
  bank                    TEXT,     -- Name der Bank
  mortgageSum             REAL,     -- Summe der Hypothek
  liborMargin             REAL,     -- Marge der Bank auf Libor
  discount                REAL,     -- Rabatt auf Fixhypothek
  yearlyAmortization      REAL,     -- Vereinbarte Amortisation
  startDate               TEXT,     -- Hypo Startdatum
  interestPaid            REAL,     -- Bisher bezahlte Zinsen
  planningHorizon         INTEGER,  -- Zeithorizont, z.B. 10 Jahre
  maxInterestOverHorizon  REAL,     -- Wie hoch darf der Zins für eine Fixhypothek über den Planungshorizont sein? (z.B. 0.5% über aktuellen Werten)
  lastInterestPaidTS      TEXT,     -- Datum wann das letzte mal paidInterest in der DB aktualisiert wurde
  lastMaxInterestResult   REAL,     -- Ergebnis der letzten Berechnung: Wie hoch dürfte der Zins für eine Fixhypothek über die verbleibende Restlaufzeit steigen?
  liborMonths             INTEGER,  -- 3 oder 6 Monate Libor Fixierung
  FOREIGN KEY(fk_customer) REFERENCES Customer(id)
);

INSERT INTO Customer VALUES(NULL, "sebastian.hubrich@gmail.com", "2090-01-01");
INSERT INTO Mortgage VALUES(NULL, 1, "Raiffeisen", 380000, 0.9, 0.2, 1000, "2014-10-1", 0, 10, 2.5, NULL, NULL, 3);