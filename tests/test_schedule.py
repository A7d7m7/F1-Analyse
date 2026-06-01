from f1_analysis.schedule import available_seasons, event_options_for_season, format_event_option


def test_available_seasons_are_selectable():
    seasons = available_seasons()

    assert 2024 in seasons
    assert 2026 in seasons
    assert seasons == sorted(seasons, reverse=True)


def test_event_options_depend_on_selected_season():
    season_2020 = event_options_for_season(2020)
    season_2024 = event_options_for_season(2024)

    assert any(event["name"] == "70th Anniversary Grand Prix" for event in season_2020)
    assert not any(event["name"] == "70th Anniversary Grand Prix" for event in season_2024)
    assert any(event["name"] == "Monaco Grand Prix" for event in season_2024)


def test_event_option_label_is_human_readable():
    event = event_options_for_season(2024)[0]
    label = format_event_option(event)

    assert label.startswith("R01 - ")
    assert "(" in label and ")" in label
