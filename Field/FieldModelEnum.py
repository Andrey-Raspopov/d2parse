from enum import Enum


class FieldModelEnum(Enum):
    fieldModelSimple = 0
    fieldModelFixedArray = 1
    fieldModelFixedTable = 2
    fieldModelVariableArray = 3
    fieldModelVariableTable = 4
