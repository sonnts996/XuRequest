import urllib.parse


class MyFile:
    file = {}

    def __init__(self):
        self.file = {
            "parentName": "",
            "parent": "",
            "isDir": True,
            "name": ""
        }

    def construct(self, folder: dict):
        if 'parentName' in folder:
            self.setParent(folder['parentName'])
        else:
            self.setParent("")

        if 'parent' in folder:
            self.setParent(folder['parent'])
        else:
            self.setParent("")

        if 'isDir' in folder:
            self.setDir(folder['isDir'])
        else:
            self.setDir(False)

        if 'name' in folder:
            self.setName(folder['name'])
        else:
            self.setName("")

    def parentName(self):
        return self.file['parentName']

    def parent(self):
        return self.file['parent']

    def isDir(self):
        return self.file['isDir']

    def name(self):
        return self.file['name']

    def identity(self):
        return urllib.parse.quote(self.parent() + "\\" + self.name())

    def setParentName(self, data: str):
        self.file['parentName'] = data

    def setParent(self, data: str):
        self.file['parent'] = data

    def setDir(self, data: bool):
        self.file['isDir'] = data

    def setName(self, data: str):
        self.file['name'] = data
