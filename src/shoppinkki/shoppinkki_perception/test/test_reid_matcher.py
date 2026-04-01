from shoppinkki_perception.reid_matcher import compare, extract_hsv_histogram


def test_extract_returns_list():
    result = extract_hsv_histogram(None, None)
    assert isinstance(result, list)


def test_compare_returns_float():
    score = compare([], [])
    assert isinstance(score, float)
