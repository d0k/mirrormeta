#!/usr/bin/env python

from optparse import OptionParser
import sys
from mirrormeta import *

parser = OptionParser(usage='usage: %prog [options] distributor file\n\te.g. %prog -g sourceforge testproject/test.tar.gz')
parser.add_option("-o", action="store", type="string", metavar="FILE", dest="filename", help="output file (default: stdout)")
parser.add_option("-m", action="store", type="string", metavar="FILE", dest="mirrorlist", default="thirdpartymirrors", help="mirror list to use (default: thirdpartymirrors)")
parser.add_option("-g", action="store_true", dest="hasgeoip", default=False, help="use geoip lookup (if available)")
parser.add_option("--md5", action="store", type="string", metavar="SUM", dest="md5sum", help="embed SUM as md5 sum")
parser.add_option("--sha1", action="store", type="string", metavar="SUM", dest="sha1sum", help="embed SUM as sha1 sum")
parser.add_option("--sig", action="store", type="string", metavar="FILE", dest="sigfile", help="embed contents of FILE as gpg signature")
(options, args) = parser.parse_args()

if len(args) != 2:
	parser.print_help()
	sys.exit(1)

if options.filename:
	output = open(options.filename, 'w')
else:
	output = sys.stdout

mirrorlist = open(options.mirrorlist)
meta = Metalink(mirrorlist, options.hasgeoip)

file = Metalinkfile(meta, args[0], args[1])

if options.md5sum:
	file.addmd5hash(options.md5sum)

if options.sha1sum:
	file.addsha1hash(options.sha1sum)

if options.sigfile:
	file.addsigfile(options.sigfile)

output.write(meta.toxml())
output.write('\n')
