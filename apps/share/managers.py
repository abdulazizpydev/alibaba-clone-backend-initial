from __future__ import annotations

from typing import Union
from rest_framework.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from share.types import ModelType


class BaseCRUDManager(models.Manager):
    def get_or_none(self, *args, **kwargs) -> Union[ModelType | None]:
        try:
            obj = self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None
        else:
            return obj

    def get_obj(self, *args, **kwargs) -> Union[ModelType, ValidationError]:
        try:
            obj = self.get(*args, **kwargs)
            return obj
        except self.model.DoesNotExist:
            raise ValidationError(_("{model_name} object not exists!").format(
                model_name=self.model.__name__),
                404
            )


class CustomMediaManager(BaseCRUDManager):
    pass
