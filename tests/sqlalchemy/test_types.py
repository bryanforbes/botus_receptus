from __future__ import annotations

from enum import Flag as _EnumFlag, auto
from typing import Protocol

import pytest
from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, registry

from botus_receptus.sqlalchemy.types import Flag, Snowflake, TSVector


class User(Protocol):
    id: Mapped[int]
    name: Mapped[str]
    search_index: Mapped[str]


@pytest.fixture
def sqlalchemy_registry() -> registry:
    return registry()


@pytest.fixture
def user_table(sqlalchemy_registry: registry) -> type[object]:
    @sqlalchemy_registry.mapped
    class User:
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        search_index = Column(TSVector(name, regconfig='pg_catalog.finnish'))

    return User


class MyFlag(_EnumFlag):
    One = auto()
    Two = auto()
    Four = auto()
    Eight = auto()


class TestSnowflake:
    @pytest.mark.parametrize(
        'bind_param,expected',
        [
            (1, '1'),
            (400, '400'),
            (None, None),
        ],
    )
    def test_process_bind_param(
        self, bind_param: int | None, expected: str | None
    ) -> None:
        snowflake = Snowflake()
        assert snowflake.process_bind_param(bind_param, object()) == expected

    @pytest.mark.parametrize(
        'result_value,expected',
        [
            ('1', 1),
            ('201293', 201293),
            (None, None),
        ],
    )
    def test_process_result_value(
        self, result_value: str | None, expected: int | None
    ) -> None:
        snowflake = Snowflake()

        assert snowflake.process_result_value(result_value, object()) == expected

    def test_copy(self) -> None:
        snowflake = Snowflake()

        assert snowflake.copy() is not snowflake


class TestTSVector:
    def test_init(self) -> None:
        tsvector = TSVector('name', 'age', regconfig='pg_catalog.simple')

        assert tsvector.columns == ('name', 'age')
        assert tsvector.options == {'regconfig': 'pg_catalog.simple'}

    def test_match(self, user_table: type[User]) -> None:
        expr = user_table.search_index.match('something')  # type: ignore

        assert str(expr.compile(dialect=postgresql.dialect())) == (
            '''users.search_index @@ plainto_tsquery('pg_catalog.finnish', '''
            '''%(search_index_1)s)'''
        )

    def test_concat(self, user_table: type[User]) -> None:
        assert str(
            user_table.search_index | user_table.search_index  # type: ignore
        ) == ('users.search_index || users.search_index')

    def test_match_concatenation(self, user_table: type[User]) -> None:
        concat = user_table.search_index | user_table.search_index  # type: ignore
        assert str(concat.match('something').compile(dialect=postgresql.dialect())) == (
            '(users.search_index || users.search_index) @@ '
            "plainto_tsquery('pg_catalog.finnish', %(param_1)s)"
        )

    def test_match_with_catalog(self, user_table: type[User]) -> None:
        expr = user_table.search_index.match(  # type: ignore
            'something', postgresql_regconfig='pg_catalog.simple'
        )
        assert str(expr.compile(dialect=postgresql.dialect())) == (
            '''users.search_index @@ plainto_tsquery('pg_catalog.simple', '''
            '''%(search_index_1)s)'''
        )


class TestFlag:
    def test_init(self) -> None:
        flag = Flag(MyFlag)

        assert flag._flag_cls is MyFlag
        assert isinstance(flag.impl, BigInteger)

    @pytest.mark.parametrize(
        'bind_param,expected',
        [
            (MyFlag.One, 1),
            (MyFlag.Two, 2),
            (MyFlag.Four, 4),
            (MyFlag.Eight, 8),
            (None, None),
        ],
    )
    def test_process_bind_param(
        self, bind_param: MyFlag | None, expected: int | None
    ) -> None:
        flag = Flag(MyFlag)

        assert flag.process_bind_param(bind_param, object()) == expected

    @pytest.mark.parametrize(
        'result_value,expected',
        [
            (1, MyFlag.One),
            (2, MyFlag.Two),
            (4, MyFlag.Four),
            (8, MyFlag.Eight),
            (None, None),
        ],
    )
    def test_process_result_value(
        self, result_value: int | None, expected: MyFlag | None
    ) -> None:
        flag = Flag(MyFlag)

        assert flag.process_result_value(result_value, object()) is expected
