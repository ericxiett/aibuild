from pecan import rest, expose

from aibuild.controllers.v1 import build, validate, release

class Controller(rest.RestController):

    build = build.ImageBuildController()
    validate = validate.ImageValidateController()
    release = release.ImageReleaseController()

    @expose()
    def index(self):
        return 'Welcome to aibuild controller!'
