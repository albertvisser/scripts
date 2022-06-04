import pathlib
import datetime
from invoke import task


# database server stuff
@task
def start_mongo(c):
    "start mongo database server"
    # c.run('sudo service mongodb start')
    c.run('sudo systemctl start mongodb.service')


@task
def stop_mongo(c):
    "stop mongo database server"
    # c.run('sudo service mongodb stop')
    c.run('sudo systemctl stop mongodb.service')


@task
def restart_mongo(c):
    "restart mongo database server"
    # c.run('sudo service mongodb restart')
    c.run('sudo systemctl restart mongodb.service')


@task
def repair_mongo(c):
    "repair mongo db"
    c.run('sudo rm /var/lib/mongodb/mongodb.lock')
    c.run('sudo mongod --dbpath /var/lib/mongodb/ --repair')
    c.run('sudo chmod 777 /var/lib/mongodb')


@task(help={'names': 'comma-separated list of database names'})
def dump_mongo(c, names=''):
    "dump mongo database(s) to a specific location"
    date = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    path = pathlib.Path('~/mongodump/{}'.format(date))
    path.expanduser().mkdir(parents=True, exist_ok=True)
    if not names:
        # c.run('mongodump -o ~/mongodump/{}/'.format(date))
        c.run('mongodump -o {}/'.format(path))
        return
    for name in names.split(','):
        # result = c.run('mongodump -d {} -o ~/mongodump/{}/'.format(name, date))
        result = c.run('mongodump -d {} -o {}/'.format(name, path))


@task
def restore_mongo(c, dirname):
    "restore mongo database(s) from given directory"
    c.run('mongorestore {}'.format(dirname))


@task
def start_pg(c):
    "start postgresql database server"
    # c.run('sudo service postgresql start')
    c.run('sudo systemctl start postgresql.service')


@task
def stop_pg(c):
    "stop postgresql database server"
    # c.run('sudo service postgresql stop')
    c.run('sudo systemctl stop postgresql.service')


@task
def restart_pg(c):
    "restart postgresql database server"
    # c.run('sudo service postgresql restart')
    c.run('sudo systemctl restart postgresql.service')


@task(help={'names': 'comma-separated list of database names'})
def dump_pg(c, names=''):
    "dump postgres database(s) to a specific location"
    timestamp = datetime.datetime.today().strftime('%Y%m%d:%H%M%S')
    date, time = timestamp.split(':', 1)
    path = pathlib.Path('~/pgdump/{}'.format(date))
    path.expanduser().mkdir(parents=True, exist_ok=True)
    if not names:
        c.run('pg_dumpall -f ~/pgdump/{}/all_{}.sql'.format(date, time))
        return
    for name in names.split(','):
        c.run('pg_dump {0} -f ~/pgdump/{1}/{0}_{2}.sql'.format(name, date, time))
