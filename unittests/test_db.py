import os
import pytest
import datetime
import types
from invoke import MockContext
import db

FIXDATE = datetime.datetime(2020,1,1)

def mock_run(self, *args):
    print(*args)


class MockDatetime:
    @classmethod
    def today(cls):
        return FIXDATE


def test_start_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.start_mongo(c)
    assert capsys.readouterr().out == 'sudo systemctl start mongodb.service\n'


def test_stop_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.stop_mongo(c)
    assert capsys.readouterr().out == 'sudo systemctl stop mongodb.service\n'


def test_restart_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restart_mongo(c)
    assert capsys.readouterr().out == 'sudo systemctl restart mongodb.service\n'


def test_repair_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.repair_mongo(c)
    assert capsys.readouterr().out == ('sudo rm /var/lib/mongodb/mongodb.lock\n'
                                       'sudo mongod --dbpath /var/lib/mongodb/ --repair\n'
                                       'sudo chmod 777 /var/lib/mongodb\n')


def test_dump_mongo(monkeypatch, capsys):
    def mock_mkdir(self, *args, **kwargs):
        print('called mkdir with args', args, kwargs)
    monkeypatch.setattr(db.pathlib.Path, 'mkdir', mock_mkdir)
    monkeypatch.setattr(db.datetime, 'datetime', MockDatetime)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.dump_mongo(c)
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True, 'exist_ok': True}\n"
                                       'mongodump -o ~/mongodump/20200101-000000/\n')
    db.dump_mongo(c, 'database')
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True, 'exist_ok': True}\n"
                                       'mongodump -d database -o ~/mongodump/20200101-000000/\n')


def test_list_mongodumps(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.list_mongodumps(c)
    assert capsys.readouterr().out == 'ls ~/mongodump\n'


def test_restore_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restore_mongo(c, 'name')
    assert capsys.readouterr().out == 'mongorestore ~/mongodump/name\n'
    db.restore_mongo(c, 'test/name')
    assert capsys.readouterr().out == 'mongorestore test/name\n'


def test_start_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.start_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl start postgresql.service\n'


def test_stop_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.stop_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl stop postgresql.service\n'


def test_restart_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restart_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl restart postgresql.service\n'


def test_dump_pg(monkeypatch, capsys):
    def mock_mkdir(self, *args, **kwargs):
        print('called mkdir with args', args, kwargs)
    monkeypatch.setattr(db.pathlib.Path, 'mkdir', mock_mkdir)
    monkeypatch.setattr(db.datetime, 'datetime', MockDatetime)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.dump_pg(c, '')
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True,"
                                       " 'exist_ok': True}\n"
                                       'pg_dumpall -f ~/pgdump/20200101/all_000000.sql\n')

    db.dump_pg(c, 'database')
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True,"
                                       " 'exist_ok': True}\n"
                                       'pg_dump database -f ~/pgdump/20200101/database_000000.sql\n')


def test_list_pgdumps(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.list_pgdumps(c)
    assert capsys.readouterr().out == 'ls -RU1 ~/pgdump\n'


def test_restore_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restore_pg(c, 'name')
    assert capsys.readouterr().out == 'filename should end in .sql\n'
    db.restore_pg(c, 'name.sql')
    assert capsys.readouterr().out == 'psql name < ~/pgdump/name.sql\n'
    db.restore_pg(c, 'test/db_name.sql')
    assert capsys.readouterr().out == 'psql db < ~/pgdump/test/db_name.sql\n'
    db.restore_pg(c, 'start/test/all_name.sql')
    assert capsys.readouterr().out == 'psql -f start/test/all_name.sql postgres\n'
