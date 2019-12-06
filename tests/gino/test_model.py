import pytest  # type: ignore
from gino.crud import CRUDModel
from gino.declarative import declarative_base

from botus_receptus.gino import Gino
from botus_receptus.gino.model import ModelMixin


@pytest.fixture
def row(mocker):
    class MockRow:
        items = mocker.Mock()

    return MockRow()


@pytest.fixture
def bind(mocker, row):
    class MockBind:
        first = mocker.CoroutineMock(return_value=row)

    return MockBind()


@pytest.fixture
def db():
    return Gino()


@pytest.fixture
def Base(db):
    return declarative_base(db, (CRUDModel, ModelMixin))


def test_model(Base):
    assert hasattr(Base, 'create_or_update')
    with pytest.raises(TypeError):
        Base.create_or_update()


@pytest.mark.asyncio
async def test_model_inherit(db, Base, row, bind):
    row.items.return_value = [('id', 0)]

    class MyModel(Base):
        __tablename__ = 'my_model'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String, nullable=False)

    assert hasattr(MyModel, 'create_or_update')
    model = await MyModel.create_or_update(bind=bind, set_=('name',), name='John Doe')
    assert isinstance(model, MyModel)
