class APIResponse:
    response = {}

    def __init__(self):
        self.response = {
            "content": [],
            "header": {},
            "status": 0,
            "url": ""
        }

    def construct(self, response: dict):
        if 'content' in response:
            self.setContent(response['content'])
        else:
            self.setContent({})

        if 'header' in response:
            self.setHeader(response['header'])
        else:
            self.setHeader({})

        if 'status' in response:
            self.setStatus(response['status'])
        else:
            self.setStatus(0)

        if 'url' in response:
            self.setURL(response['url'])
        else:
            self.setURL("")

    def content(self):
        return self.response['content']

    def header(self):
        return self.response['header']

    def status(self):
        return self.response['status']

    def url(self):
        return self.response['url']

    def setContent(self, data):
        self.response['content'] = data

    def setHeader(self, data):
        self.response['header'] = data

    def setStatus(self, data: int):
        self.response['status'] = data

    def setURL(self, data: str):
        self.response['url'] = data
