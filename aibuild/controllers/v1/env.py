from pecan import expose, rest

from aibuild.common.log_utils import LOG
from aibuild.db import api


class EnvInfoController(rest.RestController):

    def __init__(self):
        super(EnvInfoController, self).__init__()
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

    @expose('json')
    def get(self, env_name):
        LOG.info('Get env info request, env name: %s', env_name)

        try:
            env_info = self.db_api.get_env_info_by_name(env_name)
        except Exception as e:
            LOG.error('Get error %s', e.message)
            return dict(status=500, message=e.message)
        return dict(status=200, **env_info.__dict__)
