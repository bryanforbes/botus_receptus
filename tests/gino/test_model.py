from __future__ import annotations

from typing import Any

import pytest
from gino.crud import CRUDModel
from gino.declarative import declarative_base

from botus_receptus.gino import Gino
from botus_receptus.gino.model import ModelMixin

from ..types import MockerFixture


@pytest.fixture
def row(mocker: MockerFixture) -> Any:
    class MockRow:
        items = mocker.Mock()

    return MockRow()


class MockBind:
    def __init__(self, mocker: MockerFixture, row: Any) -> None:
        self.first = mocker.AsyncMock(return_value=row)


@pytest.fixture
def bind(mocker: MockerFixture, row: Any) -> Any:
    return MockBind(mocker, row)


@pytest.fixture
def db() -> Gino:
    return Gino()


@pytest.fixture
def Base(db: Gino) -> Any:
    return declarative_base(db, (CRUDModel, ModelMixin))


def test_model(Base: Any) -> None:
    assert hasattr(Base, 'create_or_update')
    with pytest.raises(TypeError):
        Base.create_or_update()


async def test_model_inherit(db: Gino, Base: Any, row: Any, bind: MockBind) -> None:
    row.items.return_value = [('id', 0)]

    class MyModel(Base):  # type: ignore
        __tablename__ = 'my_model'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)

    assert hasattr(MyModel, 'create_or_update')
    model = await MyModel.create_or_update(  # type: ignore
        bind=bind, set_=('name',), name='John Doe'
    )
    assert isinstance(model, MyModel)
