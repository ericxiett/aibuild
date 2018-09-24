import sqlalchemy
import sys

from aibuild.common.config import CONF
from aibuild.db import models


def main():

    if len(sys.argv) < 2:
        print('Please input valid subcommand: create')
        exit(1)

    if sys.argv[1] == 'create':
        create_tables()


def create_tables():
    print('This operation is DANGEROUS. Please backup database first!!!')
    url = CONF.get('DEFAULT', 'db_connection')
    print('url: %s' % url)
    engine = sqlalchemy.create_engine(url, echo=True)
    # Clean
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    sys.exit(main())
