#!/usr/bin/env python
# sfmeta.py
# generates metalink files from sf.net URLs
#
# Uses thirdpartymirrors list from Gentoo Linux (http://gentoo.org/)

from optparse import OptionParser
import sys
from urlparse import urlsplit
import mirrormeta

parser = OptionParser(usage='usage: %prog [options] sf.net URL [sf.net URL] [...]')
parser.add_option("-o", action="store", type="string", metavar="FILE",
                  dest="filename", help="output file (default: stdout)")
parser.add_option("-m", action="store", type="string", metavar="FILE",
                  dest="mirrorlist", default="thirdpartymirrors",
                  help="mirror list to use (default: thirdpartymirrors)")
(options, args) = parser.parse_args()

if len(args) == 0:
    parser.print_help()
    sys.exit(1)

if options.filename:
    output = open(options.filename, 'w')
else:
    output = sys.stdout

mirrorlist = open(options.mirrorlist)
meta = mirrormeta.metalink(mirrorlist, True)

for arg in args:
    url = urlsplit(arg)
    file = mirrormeta.metalink_file(meta, 'sourceforge', url.path[1:])

output.write(meta.toxml())
output.write('\n')
