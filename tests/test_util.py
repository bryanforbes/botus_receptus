import pytest  # type: ignore
import attr
import pendulum  # type: ignore

from botus_receptus.util import has_any_role, has_any_role_id, parse_duration


@attr.s(slots=True, auto_attribs=True)
class MockRole(object):
    id: int = 0
    name: str = ''


@attr.s(slots=True)
class MockMember(object):
    roles = attr.ib(default=attr.Factory(list))


def test_has_any_role() -> None:
    assert has_any_role(
        MockMember(
            roles=[MockRole(name='foo'), MockRole(name='bar'), MockRole(name='baz')]
        ),
        ['ham', 'spam', 'bar'],
    )
    assert not has_any_role(
        MockMember(
            roles=[MockRole(name='foo'), MockRole(name='bar'), MockRole(name='baz')]
        ),
        ['ham', 'spam', 'blah'],
    )


def test_has_any_role_id() -> None:
    assert has_any_role_id(
        MockMember(roles=[MockRole(id=1), MockRole(id=2), MockRole(id=3)]), [2, 4, 18]
    )
    assert not has_any_role_id(
        MockMember(roles=[MockRole(id=1), MockRole(id=2), MockRole(id=3)]), {28, 4, 18}
    )


@pytest.mark.parametrize(
    'duration,expected',
    [
        ('42s', pendulum.duration(seconds=42)),
        ('12m', pendulum.duration(minutes=12)),
        ('20h', pendulum.duration(hours=20)),
        ('7d', pendulum.duration(days=7)),
        ('2w', pendulum.duration(weeks=2)),
        ('1y', pendulum.duration(years=1)),
        ('12m30s', pendulum.duration(seconds=30, minutes=12)),
        ('20h5m', pendulum.duration(hours=20, minutes=5)),
        ('7d10h12s', pendulum.duration(seconds=12, days=7, hours=10)),
        ('2m1y', pendulum.duration(years=1, seconds=120)),
        (' 2m  1y ', pendulum.duration(years=1, seconds=120)),
    ],
)
def test_parse_duration(duration, expected):
    assert parse_duration(duration) == expected


@pytest.mark.parametrize(
    'duration,message',
    [
        ('42 s', 'Invalid duration'),
        ('42p', 'Invalid duration'),
        ('invalid', 'Invalid duration'),
        ('', 'No duration provided.'),
        ('   ', 'No duration provided.'),
    ],
)
def test_parse_duration_failures(duration, message):
    with pytest.raises(ValueError, message=message):
        parse_duration(duration)
