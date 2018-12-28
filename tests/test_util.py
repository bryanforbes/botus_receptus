import attr

from botus_receptus.util import has_any_role, has_any_role_id


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
