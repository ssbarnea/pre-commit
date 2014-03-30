from __future__ import absolute_import

import jsonschema
import pytest
import time
from plumbum import local

from pre_commit import git
from pre_commit.clientlib.validate_config import CONFIG_JSON_SCHEMA
from pre_commit.clientlib.validate_config import validate_config_extra
from testing.util import copy_tree_to_path
from testing.util import get_resource_path


@pytest.yield_fixture
def empty_git_dir(tmpdir):
    with local.cwd(tmpdir.strpath):
        local['git']['init']()
        yield tmpdir.strpath


def add_and_commit():
    local['git']['add', '.']()
    local['git']['commit', '-m', 'random commit {0}'.format(time.time())]()


@pytest.yield_fixture
def dummy_git_repo(empty_git_dir):
    # This is needed otherwise there is no `HEAD`
    local['touch']['dummy']()
    add_and_commit()
    yield empty_git_dir


def _make_repo(repo_path, repo_source):
    copy_tree_to_path(get_resource_path(repo_source), repo_path)
    add_and_commit()
    return repo_path


@pytest.yield_fixture
def python_hooks_repo(dummy_git_repo):
    yield _make_repo(dummy_git_repo, 'python_hooks_repo')


@pytest.yield_fixture
def node_hooks_repo(dummy_git_repo):
    yield _make_repo(dummy_git_repo, 'node_hooks_repo')


@pytest.yield_fixture
def consumer_repo(dummy_git_repo):
    yield _make_repo(dummy_git_repo, 'consumer_repo')


@pytest.yield_fixture
def prints_cwd_repo(dummy_git_repo):
    yield _make_repo(dummy_git_repo, 'prints_cwd_repo')


@pytest.yield_fixture
def config_for_node_hooks_repo(node_hooks_repo):
    config = {
        'repo': node_hooks_repo,
        'sha': git.get_head_sha(node_hooks_repo),
        'hooks': [{
            'id': 'foo',
            'files': '\.js$',
        }],
    }
    jsonschema.validate([config], CONFIG_JSON_SCHEMA)
    validate_config_extra([config])
    yield config


@pytest.yield_fixture
def config_for_python_hooks_repo(python_hooks_repo):
    config = {
        'repo': python_hooks_repo,
        'sha': git.get_head_sha(python_hooks_repo),
        'hooks': [{
            'id': 'foo',
            'files': '\.py$',
        }],
    }
    jsonschema.validate([config], CONFIG_JSON_SCHEMA)
    validate_config_extra([config])
    yield config


@pytest.yield_fixture
def config_for_prints_cwd_repo(prints_cwd_repo):
    config = {
        'repo': prints_cwd_repo,
        'sha': git.get_head_sha(prints_cwd_repo),
        'hooks': [{
            'id': 'prints_cwd',
            'files': '\.py$',
        }],
    }
    jsonschema.validate([config], CONFIG_JSON_SCHEMA)
    validate_config_extra([config])
    yield config
