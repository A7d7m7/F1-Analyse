"""Public Ergast-compatible Jolpica adapter. Never invents unavailable flags."""
import time
import requests
import pandas as pd

BASE_URL = 'https://api.jolpi.ca/ergast/f1'


def _pages(client, route, field):
    offset = 0
    output = []
    while True:
        try:
            response = client.get(f'{BASE_URL}/{route}/', params={'limit': 100, 'offset': offset}, timeout=(5, 20))
            if response.status_code == 429:
                raise RuntimeError('Limite Jolpica atteinte. Réessaie plus tard ; les données déjà chargées restent en cache.')
            response.raise_for_status()
            data = response.json()['MRData']
            races = data['RaceTable']['Races']
            page = [item for race in races for item in race.get(field, [])] if field else races
            output.extend(page)
            # Pagination for laps counts individual driver timings, not lap objects.
            count = sum(len(lap['Timings']) for lap in page) if field == 'Laps' else len(page)
            if not count:
                if offset < int(data.get('total', 0)):
                    raise RuntimeError('Réponse Jolpica incomplète : pagination interrompue.')
                break
            offset += count
            if offset >= int(data['total']):
                break
            time.sleep(.3)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError('Jolpica ne répond pas correctement. Réessaie dans quelques instants.') from exc
    return output


def load_jolpica_dataset(request):
    from f1_analysis.data_loader import _read_prepared, _write_prepared, _empty_telemetry
    if request.session_label != 'Race':
        raise ValueError('Le mode Jolpica analyse uniquement les courses (Race).')
    cached = _read_prepared(request, 'jolpica:race:v1')
    if cached is not None:
        return cached[0], _empty_telemetry(), cached[1]
    with requests.Session() as client:
        client.headers['User-Agent'] = 'F1-Analyse/1.0 (personal race analysis dashboard)'
        schedule = _pages(client, str(request.season), None)
        from f1_analysis.schedule import event_options_for_season
        event = next((r for r in schedule if r['raceName'] == request.event), None)
        if event is None:
            # Resolve through circuit location when source GP names differ.
            selected = next((r for r in event_options_for_season(request.season) if r['name'] == request.event), None)
            if selected:
                event = next((r for r in schedule if r['Circuit']['Location']['locality'].casefold() == selected['location'].casefold()), None)
        if event is None:
            raise ValueError('Grand Prix absent du calendrier Jolpica pour cette saison.')
        route = f"{request.season}/{event['round']}"
        time.sleep(.3)
        results = _pages(client, f'{route}/results', 'Results')
        if not results:
            raise ValueError('Résultats indisponibles : course future ou non encore publiée.')
        time.sleep(.3)
        timings = _pages(client, f'{route}/laps', 'Laps')
        time.sleep(.3)
        stops = _pages(client, f'{route}/pitstops', 'PitStops')
    frame = normalise(results, timings, stops, request, event['raceName'])
    metadata = dict(source='Jolpica', season=request.season, event=event['raceName'], session='Race', drivers=sorted(frame.Driver.unique().tolist()))
    _write_prepared(request, 'jolpica:race:v1', frame, metadata)
    return frame, _empty_telemetry(), metadata


def _seconds(value):
    if not value:
        return float('nan')
    result = 0.0
    for part in str(value).split(':'):
        result = result * 60 + float(part)
    return result


def normalise(results, laps, stops, request, event):
    rows = []
    for result in results:
        info = result['Driver']
        driver_id = info['driverId']
        driver_stops = [s for s in stops if s['driverId'] == driver_id]
        stop_laps = {int(s['lap']) for s in driver_stops if s.get('lap')}
        times = {int(l['number']): t for l in laps for t in l['Timings'] if t['driverId'] == driver_id}
        completed = int(result['laps'])
        # Preserve all classified drivers, including DNS/zero-lap entries.
        for number in range(1, max(completed, 1) + 1):
            timing = times.get(number, {})
            durations = [s.get('duration') for s in driver_stops if s.get('lap') and int(s['lap']) == number]
            rows.append(dict(Season=request.season, EventName=event, SessionName='Race',
                Driver=info.get('code') or driver_id, Team=result['Constructor']['name'],
                LapNumber=number, LapTimeSeconds=_seconds(timing.get('time')),
                IsPitInLap=number in stop_laps, IsPitOutLap=number - 1 in stop_laps,
                IsPitLap=number in stop_laps or number - 1 in stop_laps,
                PitDurationSeconds=sum(_seconds(d) for d in durations) if durations else float('nan'),
                OfficialPosition=int(result['position']), ResultStatus=result['status'],
                OfficialLaps=completed, OfficialPitStops=len(driver_stops),
                OfficialRaceTimeSeconds=float(result['Time']['millis']) / 1000 if result.get('Time', {}).get('millis') else float('nan'),
                PaceMode='unverified', TrackStatus=None, IsAccurate=False,
                Position=int(timing['position']) if timing.get('position') else None))
    return pd.DataFrame(rows)
