from pecan import rest

from aibuild.db import api


class ImageReleaseController(rest.RestController):

    def __init__(self):
        super(ImageReleaseController, self).__init__()
        self.dbapi = api.API()
