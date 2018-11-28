from pecan import expose, rest

from aibuild.common.log_utils import LOG
from aibuild.db import api


class EnvInfoController(rest.RestController):

    def __init__(self):
        super(OpenStackEnvInfoController, self).__init__()
        self.db_api = api.API()

    @expose('json')
    def hello(self):
        return {'msg': 'Hello!'}

    @expose('json')
    def post(self, **kwargs):
        LOG.info('New OpenStack env info post received %s', kwargs)

        env_uuid = None
        try:
            env_uuid = self.db_api.add_new_env_info(kwargs)
        except Exception as e:
            LOG.error('Got error %s', e)
            return {
                'return_value': '1',
                'message': e
            }
        finally:
            LOG.info('Add env info successfully!')
            return {
                'return_value': '0',
                'env_uuid': env_uuid
            }
