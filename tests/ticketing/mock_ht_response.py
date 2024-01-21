class MockHTResponse:
    def __init__(self,
                 json_data=None,
                 status_code=200):
        if json_data is not None:
            self.json_data = json_data
        self.status_code = status_code

    # mock json() method always returns a specific testing dictionary
    def json(self):
        return self.json_data
