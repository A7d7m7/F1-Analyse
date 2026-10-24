from types import SimpleNamespace
import pandas as pd
import pytest
from f1_analysis.jolpica import normalise, _pages
from f1_analysis.data_loader import SessionRequest
from f1_analysis.metrics import race_summary, prepare_laps
from f1_analysis.report import build_report


def sample():
    results=[dict(Driver={'driverId':'a','code':'AAA'}, Constructor={'name':'Ferrari'}, position='1', laps='3',status='Finished', Time={'millis':'180000'}),dict(Driver={'driverId':'b','code':'BBB'},Constructor={'name':'McLaren'},position='2',laps='0',status='Did not start')]
    laps=[{'number':str(i),'Timings':[{'driverId':'a','time':'1:00.000','position':'1'}]} for i in range(1,4)]
    return normalise(results,laps,[{'driverId':'a','lap':'2','duration':'22.3'}],SessionRequest(2024,'Test','Race'),'Test')


def test_unverified_pace_preserves_dns_and_official_counts():
    frame=sample()
    prepared=prepare_laps(frame)
    assert not prepared.IsCleanLap.any()
    assert prepared.IsPaceLap.sum()==1
    summary=race_summary(frame).set_index('Driver')
    assert summary.loc['BBB','Laps']==0
    assert summary.loc['AAA','PitStops']==1
    assert summary.loc['AAA','MedianPace']=='1:00.000'
    assert pd.isna(summary.loc['BBB','GapToLeaderSeconds'])


def test_pagination_counts_timings_not_laps(monkeypatch):
    monkeypatch.setattr('f1_analysis.jolpica.time.sleep',lambda _:None)
    offsets=[]
    class Client:
        def get(self,url,params,timeout):
            offsets.append(params['offset'])
            rows=[{'number':'1','Timings':[{'driverId':'a'},{'driverId':'b'}]}] if params['offset']==0 else [{'number':'2','Timings':[{'driverId':'a'}]}]
            return SimpleNamespace(status_code=200,raise_for_status=lambda:None,json=lambda:{'MRData':{'total':'3','RaceTable':{'Races':[{'Laps':rows}]}}})
    assert len(_pages(Client(),'2024/8/laps','Laps'))==2
    assert offsets==[0,2]


def test_429_is_actionable():
    class Client:
        def get(self,*args,**kwargs):
            return SimpleNamespace(status_code=429)
    with pytest.raises(RuntimeError,match='Limite Jolpica'):
        _pages(Client(),'2024',None)


def test_jolpica_report_has_capability_limits():
    html=build_report(sample(),dict(source='Jolpica',season=2024,event='Test',session='Race'),['AAA'],'AAA')
    assert 'sans filtrage Safety Car' in html
    assert 'Pneus, secteurs, télémétrie et simulation indisponibles' in html
    assert '<h2>Relais</h2>' not in html


def test_jolpica_sections_offline(monkeypatch):
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    import f1_analysis.data_loader as loader
    import streamlit as st
    st.cache_data.clear()
    frame=sample()
    monkeypatch.setattr(loader,'load_dataset',lambda *args:(frame,pd.DataFrame(),dict(source='Jolpica',season=2024,event='Test',session='Race')))
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app/dashboard.py',default_timeout=30).run()
    assert not app.exception
    for section in ['Rythme','Stratégie','Télémétrie','Simulation','Données et rapport']:
        app.radio(key='analysis_section').set_value(section).run()
        assert not app.exception,section
    app.button(key='report').click().run()
    assert not app.exception
    st.cache_data.clear()
