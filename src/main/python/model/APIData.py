"""Example construct:
   {
       "config": {
           "api": "training_comment_getlist",
           "link": {
               "delete": false,
               "id": 3,
               "link": "http://10.96.254.179:5021/api/training/",
               "name": "DAOTAO_BETA"
           },
           "param": {},
           "protocol": "GET",
           "type": "Param"
       },
       "response": {
           "content": [],
           "header": {
               "Content-Type": "application/json; charset=utf-8",
               "Date": "Wed, 22 Jul 2020 09:54:24 GMT",
               "Server": "Kestrel",
               "Transfer-Encoding": "chunked"
           },
           "status": 200,
           "url": "http://10.96.254.179:5021/api/training/training_comment_getlist"
       },
       "save": {
           "description": "",
           "folder": {
               "dir": "C:\\Users\\DEV-C2-2\\HttpRequest\\data",
               "isDir": true,
               "name": "invert"
           },
           "name": "training_comment_getlist.json"
       }
   }"""
from src.main.python.model.APIConfig import APIConfig
from src.main.python.model.APIResponse import APIResponse
from src.main.python.model.APISave import APISave


class APIData:
    data = {}

    def __init__(self):
        config = APIConfig().config
        response = APIResponse().response
        save = APISave().save
        self.data = {
            "config": config,
            "response": response,
            "save": save
        }

    def construct(self, data: dict):
        if 'config' in data:
            cfg = APIConfig()
            cfg.construct(data['config'])
            self.setConfig(cfg)
        else:
            self.setConfig(APIConfig())

        if 'response' in data:
            cfg = APIResponse()
            cfg.construct(data['response'])
            self.setResponse(cfg)
        else:
            self.setResponse(APIResponse())

        if 'save' in data:
            cfg = APISave()
            cfg.construct(data['save'])
            self.setSave(cfg)
        else:
            self.setSave(APISave())

    def config(self):
        return self.data['config']

    def parseConfig(self):
        cfg = APIConfig()
        cfg.construct(self.config())
        return cfg

    def response(self):
        return self.data['response']

    def parseReponse(self):
        res = APIResponse()
        res.construct(self.response())
        return res

    def save(self):
        return self.data['save']

    def parseSave(self):
        sve = APISave()
        sve.construct(self.save())
        return sve

    def setConfig(self, data: APIConfig):
        self.data['config'] = data.config

    def setResponse(self, data: APIResponse):
        self.data['response'] = data.response

    def setSave(self, data: APISave):
        self.data['save'] = data.save
