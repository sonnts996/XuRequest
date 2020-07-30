from src.main.python.model.MyFile import MyFile


class APISave:
    save = {}

    def __init__(self):
        self.save = {
            "description": "",
            "folder": MyFile().file,
            "name": ""
        }

    def construct(self, save: dict):
        if 'description' in save:
            self.setDescription(save['description'])
        else:
            self.setDescription("")

        if 'folder' in save:
            fld = MyFile()
            fld.construct(save['folder'])
            self.setFolder(fld)
        else:
            self.setFolder(MyFile())

        if 'name' in save:
            self.setName(save['name'])
        else:
            self.setName("")

    def description(self):
        return self.save['description']

    def folder(self):
        return self.save['folder']

    def parseFolder(self):
        fld = MyFile()
        fld.construct(self.folder())
        return fld

    def name(self):
        return self.save['name']

    def setDescription(self, data: str):
        self.save['description'] = data

    def setFolder(self, data: MyFile):
        self.save['folder'] = data.file

    def setName(self, data: str):
        self.save['name'] = data
