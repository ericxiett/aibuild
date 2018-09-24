from pecan import rest

from aibuild.db import api


class ImageValidateController(rest.RestController):

    def __init__(self):
        super(ImageValidateController, self).__init__()
        self.dbapi = api.API()
