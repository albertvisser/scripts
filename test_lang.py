import os
import pytest
import types
from invoke import MockContext
import tasks


def mock_run(self, *args):
    print(*args)


def run_in_dir(self, *args, **kwargs):
    print(*args, 'in', self.cwd)


