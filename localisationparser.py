#!/usr/bin/python

from xml.dom.minidom import parse
import xml.dom.minidom
import csv,codecs,cStringIO
import sys, argparse

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

parser = argparse.ArgumentParser(description='This script parses Qt .ts (translations files) into CSV for translating')

parser.add_argument('-i', '--input', help='Input file (.ts format)', required=True)
parser.add_argument('-o', '--output', help='Output file (outputs as CSV format)', required=True)
args = parser.parse_args()

DOMTree = xml.dom.minidom.parse(args.input)
collection = DOMTree.documentElement

messages = collection.getElementsByTagName("message")

stringList = []

for message in messages:
	source = message.getElementsByTagName('source')[0]
	print "Source: %s" % source.childNodes[0].data
	stringList.append(source.childNodes[0].data)

stringsFile = open(args.output, 'wb')
wr = UnicodeWriter(stringsFile, delimiter=';', lineterminator='\n')
for val in stringList:
	wr.writerow([val])