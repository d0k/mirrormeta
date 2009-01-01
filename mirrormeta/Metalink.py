import xml.dom.minidom

class Metalink:
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
