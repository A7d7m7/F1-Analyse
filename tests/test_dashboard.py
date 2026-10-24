from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_dashboard_sections_and_export():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app/dashboard.py', default_timeout=30)
    app.session_state['data_source'] = 'Demo locale'
    app.run()
    assert not app.exception
    for section in ['Rythme', 'Stratégie', 'Télémétrie', 'Simulation', 'Données et rapport']:
        app.radio(key='analysis_section').set_value(section).run()
        assert not app.exception, section
    app.button(key='report').click().run()
    assert not app.exception
