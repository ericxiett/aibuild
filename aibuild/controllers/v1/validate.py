from pecan import rest, expose

from aibuild.common.log_utils import LOG
from aibuild.db import api


class ImageValidateController(rest.RestController):

    def __init__(self):
        super(ImageValidateController, self).__init__()
        self.dbapi = api.API()

    @expose('json')
    def get(self, image_uuid):
        LOG.info('Get info of image %s' % image_uuid)
        try:
            image_info = self.dbapi.get_validated_image_by_uuid(image_uuid)
        except Exception as e:
            LOG.error('Got error %s' % e)
            return {
                'return_value': '1',
                'message': e
            }

        if not image_info:
            return {
                'return_value': '1',
                'message': 'Image not found'
            }
        else:
            return {
                'return_value': '0',
                'image_uuid': image_uuid,
                'image_url': image_info.get_url
            }
