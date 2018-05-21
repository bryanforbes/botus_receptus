from botus_receptus.util import unique_seen


def test_unique_seen() -> None:
    assert list(unique_seen('AaAABBBCcDAABBBcab')) == ['A', 'a', 'B', 'C', 'c', 'D', 'b']
    assert list(unique_seen('AaAABBBCcDAABBBcab', str.lower)) == ['A', 'B', 'C', 'D']
