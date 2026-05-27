import pytest
from app.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_alive(client):
    rv = client.get('/health/alive')
    assert rv.status_code == 200
    assert b'OK' in rv.data


def test_root_html_only(client):
    rv = client.get('/', headers={'Accept': 'application/json'})
    assert rv.status_code == 406


def test_root_html_accept(client):
    rv = client.get('/', headers={'Accept': 'text/html'})
    assert rv.status_code == 200
    assert b'GET /tasks' in rv.data


def test_ready_fails(client):
    rv = client.get('/health/ready')
    assert rv.status_code == 500


class MockCursor:
    def execute(self, *args, **kwargs):
        pass

    def fetchall(self):
        return [{"id": 1, "title": "Test", "status": "pending", "created_at": "now"}]

    @property
    def lastrowid(self):
        return 1


class MockConn:
    def cursor(self):
        return MockCursor()

    def commit(self):
        pass

    def close(self):
        pass


def test_tasks_get(client, monkeypatch):
    monkeypatch.setattr("app.main.get_db_connection", lambda: MockConn())
    rv = client.get('/tasks')
    assert rv.status_code == 200


def test_tasks_post(client, monkeypatch):
    monkeypatch.setattr("app.main.get_db_connection", lambda: MockConn())
    rv = client.post('/tasks', json={"title": "New Task"})
    assert rv.status_code == 201


def test_task_done(client, monkeypatch):
    monkeypatch.setattr("app.main.get_db_connection", lambda: MockConn())
    rv = client.post('/tasks/1/done')
    assert rv.status_code == 200
