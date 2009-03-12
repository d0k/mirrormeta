#!/usr/bin/env python
# mirrormeta.py
#
# Copyright (c) 2007,2009 Benjamin Kramer
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from os import path
from urlparse import urlsplit
import xml.dom.minidom

class metalink:
    def __init__(self, mirrorlist, geoip):
        self.mirrorlist = mirrorlist

        self.doc = xml.dom.minidom.Document()
        self.metalink = self.doc.createElementNS('http://www.metalinker.org/', 'metalink')
        # TODO: force xmlns in a nicer fashion
        self.metalink.setAttribute('xmlns', 'http://www.metalinker.org/')
        self.metalink.setAttribute('version', '3.0')
        self.metalink.setAttribute('generator', __name__)
        self.doc.appendChild(self.metalink)

        self.files = self.doc.createElement('files')
        self.metalink.appendChild(self.files)

        self.gi = False
        if geoip:
            import GeoIP
            self.gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

    def toxml(self):
        return self.doc.toxml()

class metalink_file:
    def __init__(self, metalink, distributor, filepath):
        self.__metalink = metalink
        metalink.mirrorlist.seek(0)
        for line in metalink.mirrorlist:
            mirrors = line.split()
            if mirrors[0] == distributor:
                break
        else:
            raise Exception('distributor %s not found.'%distributor)
        del mirrors[0]

        self.file = metalink.doc.createElement('file')
        self.file.setAttribute('name', path.basename(filepath))
        resources = metalink.doc.createElement('resources')

        for mirror in mirrors:
            url = metalink.doc.createElement('url')
            mirrorurl = urlsplit(mirror)
            url.setAttribute('type', mirrorurl.scheme)
            if metalink.gi:
                country = metalink.gi.country_code_by_name(mirrorurl.hostname)
                if country:
                    url.setAttribute('location', country.lower())
            url.appendChild(metalink.doc.createTextNode(mirror+'/'+filepath))
            resources.appendChild(url)

        self.file.appendChild(resources)
        metalink.files.appendChild(self.file)

        self.ver = False

    def __check_ver(self):
        if not self.ver:
            self.ver = self.__metalink.doc.createElement('verification')
            self.file.appendChild(self.ver)

    def __create_hash_node(self, hashtype, hashvalue):
        self.__check_ver()
        hash = self.__metalink.doc.createElement('hash')
        hash.setAttribute('type', hashtype)
        hash.appendChild(self.__metalink.doc.createTextNode(hashvalue))
        self.ver.appendChild(hash)

    def __create_sig_node(self, contents):
        self.__check_ver()
        sig = self.__metalink.doc.createElement('signature')
        sig.setAttribute('type', 'pgp')
        sig.appendChild(self.__metalink.doc.createTextNode('\n'+contents))
        self.ver.appendChild(sig)

    def add_md5_hash(self, hash):
        if len(hash) == 32:
            self.__create_hash_node('md5', hash)
        else:
            raise Exception('Invalid MD5 sum')

    def add_sha1_hash(self, hash):
        if len(hash) == 40:
            self.__create_hash_node('sha1', hash)
        else:
            raise Exception('Invalid SHA1 sum')

    def add_sig_file(self, file):
        f = open(file)
        self.__create_sig_node(f.read())
        f.close()

# Uses thirdpartymirrors list from Gentoo Linux (http://gentoo.org/)
if __name__ == "__main__":
    from optparse import OptionParser
    import sys

    parser = OptionParser(usage='usage: %prog [options] distributor file\n\te.g.' +
                          '%prog -g sourceforge testproject/test.tar.gz')
    parser.add_option("-o", action="store", type="string", metavar="FILE",
                      dest="filename", help="output file (default: stdout)")
    parser.add_option("-m", action="store", type="string", metavar="FILE",
                      dest="mirrorlist", default="thirdpartymirrors",
                      help="mirror list to use (default: thirdpartymirrors)")
    parser.add_option("-g", action="store_true", dest="hasgeoip", default=False,
                      help="use geoip lookup (if available)")
    parser.add_option("--md5", action="store", type="string", metavar="SUM",
                      dest="md5sum", help="embed SUM as md5 sum")
    parser.add_option("--sha1", action="store", type="string", metavar="SUM",
                      dest="sha1sum", help="embed SUM as sha1 sum")
    parser.add_option("--sig", action="store", type="string", metavar="FILE",
                      dest="sigfile", help="embed contents of FILE as gpg signature")
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    if options.filename:
        output = open(options.filename, 'w')
    else:
        output = sys.stdout

    mirrorlist = open(options.mirrorlist)
    meta = metalink(mirrorlist, options.hasgeoip)

    file = metalink_file(meta, args[0], args[1])

    if options.md5sum:
        file.add_md5_hash(options.md5sum)

    if options.sha1sum:
        file.add_sha1_hash(options.sha1sum)

    if options.sigfile:
        file.add_sig_file(options.sigfile)

    output.write(meta.toxml())
    output.write('\n')
