from pecan import rest, expose

from aibuild.controllers.v1 import build, validate, release, env_info


class Controller(rest.RestController):

    build = build.ImageBuildController()
    validate = validate.ImageValidateController()
    release = release.ImageReleaseController()
    env = env_info.OpenStackEnvInfoController()

    @expose()
    def index(self):
        return 'Welcome to aibuild controller!'
