import math

from stats.metrics import (bootstrap_ci, flip_rate, mcnemar_majority, paired_bootstrap_diff, pass_at, pass_at_k,
                           pass_hat, pass_hat_k, success_rate)


def test_pass_k_formulas():
    assert pass_hat_k(4, 4, 4) == 1 and pass_hat_k(4, 3, 4) == 0
    assert math.isclose(pass_hat_k(4, 2, 2), 1 / 6)
    assert pass_at_k(4, 0, 2) == 0 and pass_at_k(4, 1, 4) == 1
    assert math.isclose(pass_at_k(4, 1, 1), 0.25)


def test_pass_hat_is_never_above_pass_at():
    pt = {"a": [True, False, True, True], "b": [False] * 4, "c": [True] * 4}
    assert pass_hat(pt, 4) <= success_rate(pt) <= pass_at(pt, 4)


def test_bootstrap_contains_point_and_is_wider_for_fewer_tasks():
    big = {str(i): [i % 2 == 0] * 4 for i in range(100)}
    small = {str(i): [i % 2 == 0] * 4 for i in range(10)}
    p, lo, hi = bootstrap_ci(big)
    assert lo <= p <= hi and (hi - lo) < (bootstrap_ci(small)[2] - bootstrap_ci(small)[1])


def test_paired_tests_detect_a_clear_gain():
    a = {str(i): [False] * 4 for i in range(30)}
    b = {str(i): [True] * 4 for i in range(30)}
    d, lo, hi = paired_bootstrap_diff(a, b)
    assert d == 1 and lo > 0
    assert mcnemar_majority(a, b)["p_value"] < 0.001


def test_flip_rate():
    ga = [{"task_id": "t", "trial": i, "success": s} for i, s in enumerate([1, 1, 0, 0])]
    gb = [{"task_id": "t", "trial": i, "success": s} for i, s in enumerate([1, 0, 0, 1])]
    assert flip_rate(ga, gb) == 0.5
