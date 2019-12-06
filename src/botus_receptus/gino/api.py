from __future__ import annotations

from gino import Gino as _Gino

from .model import ModelMixin


class Gino(_Gino):
    model_base_classes = _Gino.model_base_classes + (ModelMixin,)
