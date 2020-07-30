class APILink:
    link = {}

    def __init__(self):
        self.link = {
            "delete": False,
            "id": -1,
            "url": "",
            "name": ""
        }

    def construct(self, link: dict):
        if 'delete' in link:
            self.setDelete(link['delete'])
        else:
            self.setDelete(False)

        if 'id' in link:
            self.setID(link['id'])
        else:
            self.setID(0)

        if 'url' in link:
            self.setURL(link['url'])
        else:
            self.setURL("")

        if 'name' in link:
            self.setName(link['name'])
        else:
            self.setName("")

    def delete(self):
        return self.link['delete']

    def id(self):
        return self.link['id']

    def url(self):
        return self.link['url']

    def name(self):
        return self.link['name']

    def setDelete(self, data: bool):
        self.link['delete'] = data

    def setID(self, data: int):
        self.link['id'] = data

    def setURL(self, data: str):
        self.link['url'] = data

    def setName(self, data: str):
        self.link['name'] = data
