import os
from invoke import task


# database server stuff
@task
def start_mongo(c):
    "start mongo database server"
    c.run('sudo service mongodb start')


@task
def stop_mongo(c):
    "stop mongo database server"
    c.run('sudo service mongodb stop')


@task
def restart_mongo(c):
    "restart mongo database server"
    c.run('sudo service mongodb restart')


@task
def repair_mongo(c):
    "repair mongo db"
    c.run('sudo rm /var/lib/mongodb/mongodb.lock')
    c.run('sudo mongod --dbpath /var/lib/mongodb/ --repair')
    c.run('sudo chmod 777 /var/lib/mongodb')


@task
def start_pg(c):
    "start postgresql database server"
    c.run('sudo service postgresql start')


@task
def stop_pg(c):
    "stop postgresql database server"
    c.run('sudo service postgresql stop')


@task
def restart_pg(c):
    "restart postgresql database server"
    c.run('sudo service postgresql restart')
