import sys

import xlwt

VALID_ENV_FIELDS = ['index', 'env_name', 'auth_url', 'project_domain_name',
                    'user_domain_name', 'project_name',
                    'username', 'password', 'region']
VALID_GUESTOS_FIELDS = ['index', 'name', 'base_iso', 'type',
                        'distro', 'version']

def main():
    print('Welcome to use script to generate xls template for registering env info...')
    style = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    wb = xlwt.Workbook()

    # Add env info template
    ws_envs = wb.add_sheet('envs')
    for col in range(len(VALID_ENV_FIELDS)):
        ws_envs.write(0, col, VALID_ENV_FIELDS[col], style)

    # Add guest os template
    ws_guestos = wb.add_sheet('guestos')
    for col in range(len(VALID_GUESTOS_FIELDS)):
        ws_guestos.write(0, col, VALID_GUESTOS_FIELDS[col], style)

    wb.save('aibuild.xls')


if __name__ == '__main__':
    sys.exit(main())
