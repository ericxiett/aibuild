from pecan import rest, expose

from aibuild.common.log_utils import LOG
from aibuild.db import api


class ImageTestController(rest.RestController):

    def __init__(self):
        super(ImageTestController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def post(self, **kwargs):
        LOG.info('New test log received %s', kwargs)

        try:
            log_id = self.dbapi.create_test_log(kwargs)
        except Exception as e:
            LOG.error('Got error %s', e.message)
            return dict(status=500, message=e.message)
        if not log_id:
            LOG.info('Invalid input or unknown error')
            return dict(status=500, message='Invalid input or unknown error')
        return dict(status=200, log_id=log_id)
