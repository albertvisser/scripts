"""Invoke tasks for managing databases
"""
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
    path = pathlib.Path(f'~/mongodump/{date}')
    path.expanduser().mkdir(parents=True, exist_ok=True)
    if not names:
        # c.run('mongodump -o ~/mongodump/{}/'.format(date))
        c.run(f'mongodump -o {path}/')
        return
    for name in names.split(','):
        # result = c.run('mongodump -d {} -o ~/mongodump/{}/'.format(name, date))
        result = c.run(f'mongodump -d {name}_database -o {path}/')


@task
def list_mongodumps(c):
    "list directories containing backups made using db.dump-mongo"
    c.run('ls ~/mongodump')


@task
def restore_mongo(c, dirname):
    "restore mongo database(s) from given directory (named like <EEjjmmdd-hhmmss>)"
    filepath = pathlib.Path(dirname)
    if str(filepath.parent) == '.':
        filepath = pathlib.Path('~/mongodump') / dirname
    c.run(f'mongorestore {filepath}')


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
    path = pathlib.Path(f'~/pgdump/{date}')
    path.expanduser().mkdir(parents=True, exist_ok=True)
    if not names:
        c.run(f'pg_dumpall -f ~/pgdump/{date}/all_{time}.sql')
        return
    for name in names.split(','):
        c.run(f'pg_dump {name} -f ~/pgdump/{date}/{name}_{time}.sql')


@task
def list_pgdumps(c):
    "list backups made using db.dump-pg"
    c.run('ls -RU1 ~/pgdump')


@task
def restore_pg(c, filename):
    "restore postgres database)s) from given file (named like <EEjjmmdd>/<database>-<hhmmss>.sql)"
    # breakpoint()
    filepath = pathlib.Path(filename)
    if len(filepath.parents) <= 2:
        filepath = pathlib.Path('~/pgdump') / filename
    if filepath.suffix != '.sql':
        print('filename should end in .sql')
    elif filepath.name.startswith('all'):
        c.run(f"psql -f {filepath} postgres")
    else:
        dbname = filepath.stem.split('_')[0]
        c.run(f"psql {dbname} < {filepath}")
