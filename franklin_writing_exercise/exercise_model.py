import enum
import sqlite3
from typing import Any

from PyQt5.QtCore import (
    QAbstractListModel,
    QAbstractTableModel,
    QMargins,
    QModelIndex,
    Qt,
)
from PyQt5.QtGui import QFontMetrics


@enum.unique
class ExerciseColumns(enum.Enum):
    Author = 0
    Source = 1
    Original = 2
    Notes = 3
    Rewrite = 4
    Correction = 5
    Poetry = 6
    Prose = 7


class ExerciseModel(QAbstractTableModel):
    def __init__(self, filename: str, parent=None):
        super().__init__(parent=parent)
        self._filename = filename

        self._db = sqlite3.connect(self._filename)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS FranklinExercise ("
            + ",".join(col.name + " TEXT DEFAULT ''" for col in ExerciseColumns)
            + ");"
        )

    def __del__(self):
        self._db.close()

    def get_row(self, row: int):
        return self._db.execute(
            f"SELECT * FROM FranklinExercise LIMIT 1 OFFSET ?;", (row,)
        ).fetchone()

    def set_data(self, row: int, column: ExerciseColumns, value: str):
        if self._get_value(column, row) != value:
            self._set_value(column, row, value)
            index = self.createIndex(row, column.value)
            self.dataChanged.emit(index, index, (Qt.DisplayRole, Qt.SizeHintRole))
            self._db.commit()

    # Override
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return self._db.execute("SELECT COUNT (*) FROM FranklinExercise;").fetchone()[0]

    # Override
    def columnCount(self, _parent) -> int:
        return len(ExerciseColumns)

    # Override
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            return self._get_value(ExerciseColumns(index.column()), index.row())
        if role == Qt.SizeHintRole:
            text = self._get_value(ExerciseColumns(index.column()), index.row())
            size = QFontMetrics(self.parent().font()).boundingRect(text).size()
            size = size.grownBy(QMargins(8, 8, 8, 8))
            return size

        return None

    # Override
    def headerData(
        self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole
    ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ExerciseColumns(section).name
            else:
                return str(section + 1)

        return None

    # Override
    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent.isValid() or row != self.rowCount():
            return False
        self.beginInsertRows(parent, row, row)
        self._db.execute("INSERT INTO FranklinExercise DEFAULT VALUES;")
        self.endInsertRows()
        self._db.commit()

    # Override
    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if parent.isValid() or row >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row)
        self._db.execute(
            "DELETE FROM FranklinExercise WHERE rowid=(SELECT rowid FROM FranklinExercise LIMIT 1 OFFSET ?)",
            (row,),
        )
        self.endRemoveRows()
        self._db.commit()

    def _get_value(self, column: ExerciseColumns, row: int) -> str:
        return self._db.execute(
            f"SELECT {column.name} FROM FranklinExercise LIMIT 1 OFFSET ?;", (row,)
        ).fetchone()[0]

    def _set_value(self, column: ExerciseColumns, row: int, value: str):
        self._db.execute(
            f"UPDATE FranklinExercise SET {column.name} = ? WHERE rowid=(SELECT rowid FROM FranklinExercise LIMIT 1 OFFSET ?);",
            (value, row),
        )
        self._db.commit()

    class UniqueColumnModel(QAbstractListModel):
        def __init__(self, parent_model, column) -> None:
            super().__init__(parent=parent_model)
            self._db = parent_model._db
            self._column = column

        def rowCount(self, parent: QModelIndex) -> int:
            if parent.isValid():
                return 0
            return self._db.execute(
                f"SELECT COUNT (DISTINCT {self._column.name}) FROM FranklinExercise"
            ).fetchone()[0]

        def data(self, index: QModelIndex, role: int):
            if role == Qt.DisplayRole:
                col = self._column.name
                return self._db.execute(
                    f"SELECT T.{col} FROM (SELECT DISTINCT {col} FROM FranklinExercise ORDER BY {col}) AS T LIMIT 1 OFFSET ?",
                    (index.row(),),
                ).fetchone()[0]
            return None