import sqlite3

class LocationDb():

    def __init__(self):
        self.dbfilename = 'locations.db'
        self.connection = sqlite3.connect(self.dbfilename)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='locations' ''')
        if not self.cursor.fetchone()[0] == 1:
            self.createDb()

    def createDb(self) -> bool:
        sql = """CREATE TABLE locations (facility TEXT,
                                         latitude REAL,
                                         longitude REAL,
                                         state TEXT,
                                         street TEXT,
                                         zip TEXT,
                                         distance REAL)"""
        self.cursor.execute(sql)

    def findLocation(self, location: str) -> list:
        loc = location[:8] + '%'
        sql = f"SELECT * from locations where facility like '{loc}'"
        #r = self.cursor.execute(sql, [location[:8] + '%',])
        r = self.cursor.execute(sql)
        return r.fetchall()


    def addLocation(self,
                    facility: str,
                    street: str,
                    city: str,
                    state: str,
                    zip: str,
                    latitude: float,
                    longitude: float,
                    distance: float) -> None:
        sql = 'INSERT INTO locations (facility, latitude, longitude, state, street, zip, distance) \
               VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(sql,
                            [facility,
                             latitude,
                             longitude,
                             state,
                             street,
                             zip,
                             distance])
        self.connection.commit()
