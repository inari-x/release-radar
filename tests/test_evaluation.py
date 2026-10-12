from release_radar.evaluation import Metrics, compute_metrics


def test_counts_each_outcome():
    results = [(True, True), (True, False), (False, True), (False, False), (False, False)]
    m = compute_metrics(results)
    assert m.true_positives == 1     # truly breaking, AI caught it
    assert m.false_negatives == 1    # truly breaking, AI missed it
    assert m.false_positives == 1    # not breaking, AI raised a false alarm
    assert m.true_negatives == 2     # not breaking, AI agreed


def test_precision_and_recall():
    m = Metrics(true_positives=6, false_positives=4, false_negatives=2, true_negatives=8)
    assert m.precision == 0.6
    assert m.recall == 0.75


def test_no_alarms_means_zero_precision_not_a_crash():
    m = Metrics(true_positives=0, false_positives=0, false_negatives=3, true_negatives=5)
    assert m.precision == 0.0