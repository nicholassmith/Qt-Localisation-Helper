#!/usr/bin/python

from xml.dom.minidom import parse
import xml.dom.minidom
import csv,codecs,cStringIO
import sys,argparse

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

parser = argparse.ArgumentParser(description='This script parses a CSV into a QT .ts file for translations')
parser.add_argument('-i', '--input', help='Input file (.csv format)', required=True)
parser.add_argument('-o', '--output', help='Output file (.ts used for generating original CSV', required=True)
args = parser.parse_args()

stringsFile = open(args.input, 'rb')
ur = UnicodeReader(stringsFile, delimiter=',', lineterminator='\n')

csvEntries = []

for row in ur:
    csvEntries.append(row)

DOMTree = xml.dom.minidom.parse(args.output)
collection = DOMTree.documentElement

messages = collection.getElementsByTagName("message")

print messages

for x in range(len(messages)):
    print x
    message = messages[x]
    print message
    translation = message.getElementsByTagName('translation')[0]
    
    text = DOMTree.createTextNode(csvEntries[x][1])
    translation.appendChild(text)

    print translation.tagName
    print csvEntries[x][1]

    print translation.firstChild

    translation.replaceChild(translation.firstChild, text)

with codecs.open(args.output, 'w', encoding='utf8') as f1:
    DOMTree.writexml(f1)
