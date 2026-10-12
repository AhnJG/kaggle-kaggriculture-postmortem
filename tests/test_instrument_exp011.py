import copy

from tools.instrument import Counters, _Instrumentation, attribute_drop, drop_event_summary


def test_attribution_matches_engine_order_without_mutating_input():
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    private = {'shed': {'WHEAT': 98}, 'inventories': [{'MILK': 3, 'WOOL': 2}, {'WHEAT': 4}]}
    before = copy.deepcopy(private)
    event = attribute_drop(private, 100, player=1, day=8, step=215,
                           positions=[[4, 4], [9, 9]], last_ops=['DROP', 'HARVEST'],
                           board_size=10, full_turns=2, sell_lines=[], sell_filled=0)
    assert private == before
    K._drop_inventories_to_shed(private, 100)
    assert private['shed'] == {'WHEAT': 98, 'MILK': 2}
    assert event['deposited'] == {'MILK': 2}
    assert event['discarded'] == {'MILK': 1, 'WOOL': 2, 'WHEAT': 4}
    assert event['discarded_by_unit'] == [3, 4]
    assert drop_event_summary([event])['class_counts'] == {
        'ROOM_PARTIAL|ADJACENT|DEPOSIT_ATTEMPTED': 3,
        'ROOM_PARTIAL|REMOTE|NO_DEPOSIT_ATTEMPT': 4}


def test_full_shed_class_and_zero_loss_event():
    kwargs = dict(player=0, day=0, step=23, positions=[[4, 4]], last_ops=['PASS'],
                  board_size=10, full_turns=0, sell_lines=[], sell_filled=0)
    event = attribute_drop({'shed': {'WHEAT': 100}, 'inventories': [{'MILK': 2}]}, 100, **kwargs)
    assert event['losses'][0]['class'] == 'ROOM_ZERO|ADJACENT|NO_DEPOSIT_ATTEMPT'
    empty = attribute_drop({'shed': {}, 'inventories': [{}]}, 100, **kwargs)
    assert empty['discarded_total'] == 0
    assert empty['losses'] == []


def test_drop_discards_but_place_retains_overflow_and_animal_is_not_loss():
    for action, tile, item, expected_loss, expected_left in [
        (['DROP'], None, 'MILK', 3, 0),
        (['PLACE', 'MILK', 5], None, 'MILK', 0, 3),
        (['PLACE', 'COW'], {'kind': 'PASTURE'}, 'COW', 0, 4),
    ]:
        inst = _Instrumentation()
        farm = {'farmer': [4, 4], 'hands': [], 'tiles': [[None]*10 for _ in range(10)]}
        farm['tiles'][4][4] = tile
        private = {'shed': {'WHEAT': 98}, 'inventories': [{item: 5}]}
        inst.install()
        try:
            inst.K._apply_unit_action(farm, private, 0, action, 10, 0, 24, 100)
        finally:
            inst.uninstall()
        counter = inst.counters[0]
        assert counter.shed_discarded_inday_drop + counter.shed_discarded_inday_place == expected_loss
        assert private['inventories'][0].get(item, 0) == expected_left
        assert counter.shed_discarded == 0  # existing end-of-day metric unchanged


def test_diagnostic_counters_do_not_change_release_gate():
    c = Counters(shed_discarded_inday_drop=5, shed_discarded_inday_place=2)
    assert c.is_clean()
    assert c.gate_reasons() == []
