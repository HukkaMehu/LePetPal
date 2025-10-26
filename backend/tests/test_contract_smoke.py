import json
import re
import time
from backend.app import create_app


def test_health():
    app = create_app()
    client = app.test_client()

    r = client.get('/health')
    assert r.status_code == 200
    data = r.get_json()
    assert {'status', 'api', 'version'} <= set(data.keys())


def test_video_feed_headers():
    app = create_app()
    client = app.test_client()

    r = client.get('/video_feed')
    assert r.status_code == 200
    ctype = r.headers.get('Content-Type', '')
    assert 'multipart/x-mixed-replace' in ctype
    assert 'boundary=frame' in ctype


def test_command_accept_and_status_flow():
    app = create_app()
    client = app.test_client()

    # Accept
    r = client.post('/command', json={'prompt': 'pick up the ball', 'options': {}})
    assert r.status_code in (200, 202)
    req_id = r.get_json()['request_id']

    # Poll status until final state (with a short timeout)
    deadline = time.time() + 5.0
    final = None
    while time.time() < deadline:
        s = client.get(f'/status/{req_id}')
        assert s.status_code == 200
        body = s.get_json()
        if body.get('state') in ('succeeded', 'failed', 'aborted'):
            final = body['state']
            break
        time.sleep(0.2)
    assert final in ('succeeded', 'failed', 'aborted')


def test_busy_and_invalid():
    app = create_app()
    client = app.test_client()

    # Start one that keeps the worker busy briefly
    r1 = client.post('/command', json={'prompt': 'pick up the ball', 'options': {}})
    assert r1.status_code in (200, 202)

    # Second should return 409 busy
    r2 = client.post('/command', json={'prompt': 'get the treat', 'options': {}})
    assert r2.status_code == 409

    # Invalid prompt returns 400
    r3 = client.post('/command', json={'prompt': 'dance', 'options': {}})
    assert r3.status_code == 400


def test_dispense_and_speak():
    app = create_app()
    client = app.test_client()

    d = client.post('/dispense_treat', json={'duration_ms': 100})
    assert d.status_code == 200
    assert d.get_json()['status'] == 'ok'

    s = client.post('/speak', json={'text': 'Good dog!'})
    assert s.status_code == 200
    assert s.get_json()['status'] == 'ok'
