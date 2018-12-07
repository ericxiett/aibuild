from pecan import rest, expose

from aibuild.controllers.v1 import build, test, release, env, guestos


class Controller(rest.RestController):

    build = build.ImageBuildController()
    test = test.ImageTestController()
    release = release.ImageReleaseController()
    env = env.EnvInfoController()
    guestos = guestos.GuestOSController()

    @expose()
    def index(self):
        return 'Welcome to aibuild controller!'
