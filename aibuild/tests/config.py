# Server Specific Configurations
server = {
    'port': '9753',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'aibuild.controllers.root.RootController',
    'modules': ['aibuild'],
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}
