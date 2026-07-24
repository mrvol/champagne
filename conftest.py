import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'champagne.settings')
django.setup()

from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment, teardown_test_environment


def pytest_configure(config):
    setup_test_environment()
    config._django_runner = DiscoverRunner()
    config._django_db_config = config._django_runner.setup_databases()


def pytest_unconfigure(config):
    config._django_runner.teardown_databases(config._django_db_config)
    teardown_test_environment()
