from pecan import rest, expose

from aibuild.common.log_utils import LOG
from aibuild.db import api


class ImageBuildController(rest.RestController):

    def __init__(self):
        super(ImageBuildController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def hello(self):
        return {'msg': 'Hello!'}

    @expose('json')
    def post(self, **kwargs):
        LOG.info('New build log received %s', kwargs)

        image_uuid = None
        try:
            image_uuid = self.dbapi.add_build_log(kwargs)
        except Exception as e:
            LOG.error('Got error %s', e)
            return {
                'return_value': '1',
                'image_name': kwargs.get('image_name'),
                'message': e
            }
        finally:
            LOG.info('Add build log successfully!')
            return {
                'return_value': '0',
                'image_uuid': image_uuid,
                'image_name': kwargs.get('image_name')
            }
