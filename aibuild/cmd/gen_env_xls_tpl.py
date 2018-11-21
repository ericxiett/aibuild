import sys

import xlwt

VALID_FIELDS = ['index', 'env_name', 'auth_url', 'project_domain_name', 'user_domain_name', 'project_name',
                'username', 'password', 'region']

def main():
    print('Welcome to use script to generate xls template for registering env info...')
    style = xlwt.easyxf('font: name Times New Roman, color-index green, bold on',
                         num_format_str='#,##0')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('envs')
    for col in range(len(VALID_FIELDS)):
        ws.write(0, col, VALID_FIELDS[col], style)
    wb.save('env_info.xls')


if __name__ == '__main__':
    sys.exit(main())
