import json

import pytest
from typer.testing import CliRunner

from app import (
    DB_READ_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    task_tracker,
)

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ['--version'])
    assert result.exit_code == 0
    assert f'{__app_name__} v{__version__}\n' in result.stdout

@pytest.fixture
def mock_json_file(tmp_path):
    todo = [{'Description': 'Get some milk.', 'Property': 2, 'Done': False}]
    db_file = tmp_path / 'todo.json'
    with db_file.open('w') as db:
        json.dump(todo, db, indent=4)
    return db_file

test_data1 = {
    "description": ["Clean", "the", "house"],
    "priority": 1,
    "todo": {
        "Description": "Clean the house.",
        "Priority": 1,
        "Done": False,
    },
}
test_data2 = {
    "description": ["Wash the car"],
    "priority": 2,
    "todo": {
        "Description": "Wash the car.",
        "Priority": 2,
        "Done": False,
    },
}

@pytest.mark.parametrize(
    "description, priority, expected",
    [
        pytest.param(
            test_data1["description"],
            test_data1["priority"],
            (test_data1["todo"], SUCCESS),
        ),
        pytest.param(
            test_data2["description"],
            test_data2["priority"],
            (test_data2["todo"], SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, description, priority, expected):
    todoer = task_tracker.Todoer(mock_json_file)
    assert todoer.add(description, priority) == expected
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 2
    

@pytest.fixture
def misspell_json_file(tmp_path):
    todo = [{'Description': 'Get some milk 3.', 'Priority': 2, 'Done': False}]
    db_file = tmp_path / 'todo.json'
    with db_file.open('w') as db:
        json.dump(todo, db, indent=4)
    return db_file

test_data1 = {
    "todo_id": 1,
    "description": ["Get some milk"],
    "todo": {
        "Description": "Get some milk.",
        "Priority": 2,
        "Done": False
    },
}

@pytest.mark.parametrize(
    "todo_id, description, expected",
    [
        pytest.param(
            test_data1["todo_id"],
            test_data1["description"],
            (test_data1["todo"], SUCCESS),
        ),
    ],
)
def test_update(misspell_json_file, todo_id, description, expected):
    todoer = task_tracker.Todoer(misspell_json_file)
    assert todoer.update(todo_id, description) == expected
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 1
