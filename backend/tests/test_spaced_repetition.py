from datetime import datetime, timedelta

from app.services.spaced_repetition import calculate_sm2


def test_first_successful_review_sets_interval_to_one():
    ef, interval, reps, _ = calculate_sm2(score=4, ease_factor=2.5, interval=0, repetitions=0)
    assert interval == 1
    assert reps == 1
    assert ef >= 1.3


def test_second_successful_review_sets_interval_to_six():
    _, interval, reps, _ = calculate_sm2(score=5, ease_factor=2.5, interval=1, repetitions=1)
    assert interval == 6
    assert reps == 2


def test_subsequent_review_multiplies_interval_by_ease_factor():
    # repetitions >= 2 : new_interval = round(interval * new_ease_factor)
    ef, interval, reps, _ = calculate_sm2(score=4, ease_factor=2.0, interval=10, repetitions=2)
    assert reps == 3
    assert interval == int(round(10 * ef))
    assert interval > 10


def test_failed_review_resets_progress():
    _, interval, reps, _ = calculate_sm2(score=1, ease_factor=2.5, interval=20, repetitions=5)
    assert reps == 0
    assert interval == 1


def test_ease_factor_never_drops_below_floor():
    ef, _, _, _ = calculate_sm2(score=0, ease_factor=1.3, interval=1, repetitions=0)
    assert ef == 1.3


def test_next_review_is_scheduled_in_the_future():
    before = datetime.utcnow()
    _, interval, _, next_review = calculate_sm2(score=5, ease_factor=2.5, interval=1, repetitions=1)
    assert next_review > before
    assert next_review <= before + timedelta(days=interval, seconds=5)
