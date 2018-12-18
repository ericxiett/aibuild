from pecan import rest, expose

from aibuild.common.log_utils import LOG
from aibuild.db import api


class ImageReleaseController(rest.RestController):

    def __init__(self):
        super(ImageReleaseController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def post(self, **body):
        LOG.info('Get release post request %s', body)

        try:
            release_log = self.dbapi.create_release_log(**body)
        except Exception as e:
            LOG.error('Get error %s', e.message)
            return dict(status=500, message=e.message)
        return dict(status=200, **release_log.__dict__)
