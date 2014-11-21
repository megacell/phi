__author__ = 'lei'
from lxml import etree
import cStringIO as strio
from django.db import connection

class DBWriter:
    def __init__(self, dbname, create_query, batch_size = 10000):
        self.sb = strio.StringIO()
        self.count = 0
        self.create_query = create_query
        self.cursor = connection.cursor()
        self.batch_size = batch_size
        self.dbname = dbname

    def createDB(self):
        self.cursor.execute(self.create_query)

    def writeToDb(self):
        self.sb.reset()
        self.cursor.copy_from(self.sb, self.dbname)
        self.sb.close()
        self.sb = strio.StringIO()
        self.count = 0

    def add(self, row):
        self.count += 1
        self.sb.write(row)
        if self.count > self.batch_size == 0:
            self.writeToDb()

    def flush(self):
        self.writeToDb()
class TravelTimes:
    def __init__(self):
        self.startTime = dict()
        self.endTime = dict()

    def addStart(self, key, time):
        self.startTime[key] = time

    def addEnd(self, key, time):
        self.endTime[key] = time

    def getTravelTimes(self):
        startkeys = set(self.startTime.keys())
        startkeys.intersection_update(self.endTime.keys())
        travelTimes = dict()
        for i in startkeys:
            travelTimes[i] = self.endTime[i]-self.startTime[i]
        return travelTimes

class EventsLoader:
    def __init__(self, path):
        self.eventpath = path

    @staticmethod
    def isVehicle(element):
        return 'vehicle' in element.attrib.keys() and element.attrib['type'] == 'left link'

    def load(self):
        with open(self.eventpath) as f:
            tree = etree.iterparse(f)

            eventswriter = DBWriter('events', '''
                DROP TABLE IF EXISTS events;
                CREATE TABLE events(time float, link int, vehicle int, person int);
                ''')
            eventswriter.createDB()
            for i, (action, element) in enumerate(tree):
                if element.tag =='event' and EventsLoader.isVehicle(element):
                    a = element.attrib
                    eventswriter.add('\t'.join([a['time'], a['link'], a['vehicle'], a['person']])+'\n')
                element.clear()

            eventswriter.flush()
class LinkTimingLoader:
    def __init__(self, path):
        self.eventpath = path

    @staticmethod
    def isLeftLink(element):
        return 'vehicle' in element.attrib.keys() and element.attrib['type'] == 'left link'
    @staticmethod
    def isEnterLink(element):
        return 'vehicle' in element.attrib.keys() and element.attrib['type'] == 'entered link'
    def load(self):
        with open(self.eventpath) as f:
            tree = etree.iterparse(f)

            eventswriter = DBWriter('events', '''
                DROP TABLE IF EXISTS events CASCADE;
                CREATE TABLE events(time float, link int, person int, entered int);
                ''')
            eventswriter.createDB()
            for i, (action, element) in enumerate(tree):
                a = element.attrib
                if element.tag =='event' and LinkTimingLoader.isLeftLink(element):
                    eventswriter.add('\t'.join([str(-float(a['time'])), a['link'], a['person'], '0'])+'\n')
                elif element.tag =='event' and LinkTimingLoader.isEnterLink(element):
                    eventswriter.add('\t'.join([a['time'], a['link'], a['person'], '1'])+'\n')
                element.clear()

            eventswriter.flush()
el = LinkTimingLoader("/home/lei/traffic/datasets/Phi/500k_run0.10.events.xml")
el.load()