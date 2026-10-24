from unittest.mock import Mock
from f1_analysis.f1_auth import F1Login


def test_browser_url_is_only_output_exposed():
    login=F1Login()
    process=Mock()
    process.stdout=iter(['private token should not appear\n', 'https://f1login.fastf1.dev?port=12345\n'])
    # A file-like stream is used in production.
    from io import StringIO
    process.stdout=StringIO('private token\nhttps://f1login.fastf1.dev?port=12345\n')
    login.process=process
    login._read_url(process)
    assert login.url=='https://f1login.fastf1.dev?port=12345'


def test_cancel_terminates_pending_login():
    login=F1Login()
    login.process=Mock()
    login.process.poll.return_value=None
    login.url='https://f1login.fastf1.dev?port=12345'
    login.cancel()
    login.process.terminate.assert_called_once()
    assert login.url is None


def test_fastf1_disconnected_does_not_start_loading(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    monkeypatch.setattr(F1Login,'connected',lambda self:False)
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app/dashboard.py',default_timeout=20)
    app.session_state['data_source']='FastF1'
    app.run()
    assert not app.exception
    assert any('Connecte ton compte' in info.value for info in app.info)
    assert app.button(key='connect_f1')
