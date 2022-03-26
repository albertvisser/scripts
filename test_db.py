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


def test_restore_mongo(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restore_mongo(c, 'name')
    assert capsys.readouterr().out == 'mongorestore name\n'


def test_start_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.start_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl start postgres.service\n'


def test_stop_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.stop_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl stop postgres.service\n'


def test_restart_pg(monkeypatch, capsys):
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.restart_pg(c)
    assert capsys.readouterr().out == 'sudo systemctl restart postgres.service\n'


def test_dump_pg(monkeypatch, capsys):
    def mock_mkdir(self, *args, **kwargs):
        print('called mkdir with args', args, kwargs)
    monkeypatch.setattr(db.pathlib.Path, 'mkdir', mock_mkdir)
    monkeypatch.setattr(db.datetime, 'datetime', MockDatetime)
    monkeypatch.setattr(MockContext, 'run', mock_run)
    c = MockContext()
    db.dump_pg(c, '')
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True, 'exist_ok': True}\n"
                                       'pg_dumpall -f ~/pgdump/20200101/all_000000.sql\n')

    db.dump_pg(c, 'database')
    assert capsys.readouterr().out == ("called mkdir with args () {'parents': True, 'exist_ok': True}\n"
                                       'pg_dump database -f ~/pgdump/20200101/database_000000.sql\n')
