from src.main.python.model.APILink import APILink


class APIConfig:
    config = {}

    def __init__(self):
        self.config = {
            "api": "",
            "link": APILink().link,
            "param": {},
            "protocol": "",
            "type": "",
            "format": []
        }

    def construct(self, config: dict):
        if 'api' in config:
            self.setAPI(config['api'])
        else:
            self.setAPI("")

        if 'link' in config:
            lnk = APILink()
            lnk.construct(config['link'])
            self.setLink(lnk)
        else:
            self.setLink(APILink())

        if 'param' in config:
            self.setParam(config['param'])
        else:
            self.setParam({})

        if 'protocol' in config:
            self.setProtocol(config['protocol'])
        else:
            self.setProtocol("")

        if 'type' in config:
            self.setType(config['type'])
        else:
            self.setType("")

        if 'format' in config:
            self.setFormat(config['format'])
        else:
            self.setFormat([])

    def api(self):
        return self.config['api']

    def link(self):
        return self.config['link']

    def parseLink(self):
        lnk = APILink()
        lnk.construct(self.link())
        return lnk

    def param(self):
        return self.config['param']

    def protocol(self):
        return self.config['protocol']

    def type(self):
        return self.config['type']

    def format(self):
        return self.config['format']

    def setAPI(self, data: str):
        self.config['api'] = data

    def setLink(self, data: APILink):
        self.config['link'] = data.link

    def setParam(self, data):
        self.config['param'] = data

    def setProtocol(self, data: str):
        self.config['protocol'] = data

    def setType(self, data: str):
        self.config['type'] = data

    def setFormat(self, data: list):
        self.config['format'] = data
