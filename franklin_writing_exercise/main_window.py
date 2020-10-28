import pathlib
import random
from PyQt5.QtGui import QColor

import appdirs
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtCore import pyqtSlot as slot
from PyQt5.QtWidgets import (
    QCompleter,
    QGridLayout, QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QTabBar,
    QTableView,
)

from franklin_writing_exercise.exercise_model import ExerciseColumns, ExerciseModel

from . import ui_main_window


class MainWindow(QMainWindow, ui_main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        data_dir = pathlib.Path(appdirs.user_data_dir("franklin_writing_exercise"))
        data_dir.mkdir(parents=True, exist_ok=True)
        data_path = data_dir / "exercises.db"
        self._model = ExerciseModel(str(data_path), parent=self)
        self._author_completer = QCompleter(self._model, self)
        self._source_completer = QCompleter(self._model, self)

        self._step_handlers = (
            self._step_take_notes,
            self._step_rewrite,
            self._step_corrections,
            self._step_poetry,
            self._step_to_prose,
            self._step_jumble,
        )

        self.setupUi(self)

    def setupUi(self, obj):
        super().setupUi(obj)

        self._editors = (
            (ExerciseColumns.Author, self.edit_author),
            (ExerciseColumns.Source, self.edit_source),
            (ExerciseColumns.Original, self.edit_original),
            (ExerciseColumns.Notes, self.edit_notes),
            (ExerciseColumns.Rewrite, self.edit_rewrite),
            (ExerciseColumns.Correction, self.edit_corrections),
            (ExerciseColumns.Poetry, self.edit_poetry),
            (ExerciseColumns.Prose, self.edit_prose),
        )

        self.tabbar = QTabBar()
        self.tabbar.addTab("1. Take Notes")
        self.tabbar.addTab("2. Reconstruct")
        self.tabbar.addTab("3. Corrections")
        self.tabbar.addTab("4. As Poetry")
        self.tabbar.addTab("5. Back to Prose")
        self.tabbar.addTab("6. Jumble")
        self.tabbar_container.setLayout(QGridLayout())
        self.tabbar_container.layout().addWidget(self.tabbar)
        self.tabbar.tabBarClicked.connect(self._on_tabbar_clicked)

        self.actionExit.triggered.connect(self.close)
        self.actionRemove.triggered.connect(self._on_action_remove)
        self.actionNew.triggered.connect(self._on_action_new)

        self.edit_author.textEdited.connect(self._on_edit_author_edited)
        self.edit_source.textEdited.connect(self._on_edit_source_edited)
        self.edit_corrections.textChanged.connect(self._on_edit_corrections_edited)
        self.edit_notes.textChanged.connect(self._on_edit_notes_edited)
        self.edit_original.textChanged.connect(self._on_edit_original_edited)
        self.edit_poetry.textChanged.connect(self._on_edit_poetry_edited)
        self.edit_prose.textChanged.connect(self._on_edit_prose_edited)
        self.edit_rewrite.textChanged.connect(self._on_edit_rewrite_edited)

        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.clicked.connect(self._on_table_view_clicked)

        self.btn_jumble.clicked.connect(self._on_jumble_clicked)
        self.btn_answer.clicked.connect(self._on_answer_clicked)
        self.list_widget_jumble.setSpacing(8)
        self.list_widget_answer.setSpacing(8)

        self._msgbox = QMessageBox(
            QMessageBox.Question,
            "Copy from rewrite?",
            "There are contents in the correction box. Do you want to overwrite it with notes from the previous step?",
            QMessageBox.Yes | QMessageBox.No,
            self,
        )

        self.table_view.setModel(self._model)

        displayed_columns = {
            ExerciseColumns.Author,
            ExerciseColumns.Source,
            ExerciseColumns.Original,
        }
        for column in (col for col in ExerciseColumns if col not in displayed_columns):
            self.table_view.setColumnHidden(column.value, True)

        self.table_view.horizontalHeader().setStretchLastSection(True)

        if self._model.rowCount() == 0:
            self._on_action_new()
        self.table_view.clicked.emit(self._model.index(0, 0))
        self.table_view.adjustSize()
        self.table_view.resizeColumnToContents(ExerciseColumns.Author.value)
        self.table_view.resizeColumnToContents(ExerciseColumns.Source.value)

        self._author_completer.setCompletionColumn(ExerciseColumns.Author.value)
        self._author_completer.setCompletionMode(QCompleter.PopupCompletion)
        self._author_completer.setCompletionRole(Qt.DisplayRole)
        self._source_completer.setCompletionColumn(ExerciseColumns.Source.value)
        self._source_completer.setCompletionMode(QCompleter.PopupCompletion)
        self._source_completer.setCompletionRole(Qt.DisplayRole)

        self.edit_author.setCompleter(self._author_completer)
        self.edit_source.setCompleter(self._source_completer)

    @slot(int)
    def _on_tabbar_clicked(self, index: int):
        if 0 <= index < 6:
            self._step_handlers[index]()
        else:
            raise ValueError("Tab index out of ranges")

    @slot()
    def _on_action_remove(self):
        selected = self.table_view.currentIndex()
        self._model.removeRow(selected.row())

    @slot()
    def _on_action_new(self):
        self._model.insertRow(self._model.rowCount())
        self.table_view.adjustSize()
        self.table_view.resizeColumnToContents(ExerciseColumns.Author.value)
        self.table_view.resizeColumnToContents(ExerciseColumns.Source.value)
        self.table_view.clicked.emit(self._model.index(self._model.rowCount() - 1, 0))

    @slot(str)
    def _on_edit_author_edited(self, value: str):
        selected = self.table_view.currentIndex().row()
        self._model.set_data(selected, ExerciseColumns.Author, value)
        self.table_view.adjustSize()
        self.table_view.resizeColumnToContents(ExerciseColumns.Author.value)

    @slot(str)
    def _on_edit_source_edited(self, value: str):
        selected = self.table_view.currentIndex().row()
        self._model.set_data(selected, ExerciseColumns.Source, value)
        self.table_view.adjustSize()
        self.table_view.resizeColumnToContents(ExerciseColumns.Source.value)

    @slot()
    def _on_edit_corrections_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_corrections.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Correction, value)

    @slot()
    def _on_edit_notes_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_notes.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Notes, value)

    @slot()
    def _on_edit_original_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_original.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Original, value)

    @slot()
    def _on_edit_poetry_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_poetry.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Poetry, value)

    @slot()
    def _on_edit_prose_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_prose.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Prose, value)

    @slot()
    def _on_edit_rewrite_edited(self):
        selected = self.table_view.currentIndex().row()
        value = self.edit_rewrite.toPlainText()
        self._model.set_data(selected, ExerciseColumns.Rewrite, value)

    @slot(QModelIndex)
    def _on_table_view_clicked(self, current: QModelIndex):
        if not current.isValid():
            for (_, w) in self._editors:
                w.setText("")
                w.parent().setEnabled(False)
        else:
            data = self._model.get_row(current.row())
            for column, widget in self._editors:
                widget.setText(data[column.value])
            self._step_take_notes()

    @slot()
    def _on_jumble_clicked(self):
        note_lines = self._get_note_as_lines()
        random.shuffle(note_lines)
        self.list_widget_jumble.clear()
        for line in note_lines:
            item = QListWidgetItem(line)
            color = f"#50{hash(line) & 0xFFFFFF :X}"
            item.setBackground(QColor(color))
            self.list_widget_jumble.addItem(item)
        self.list_widget_answer.setVisible(False)

    @slot()
    def _on_answer_clicked(self):
        note_lines = self._get_note_as_lines()
        self.list_widget_answer.clear()
        for line in note_lines:
            item = QListWidgetItem(line)
            color = f"#50{hash(line) & 0xFFFFFF :X}"
            item.setBackground(QColor(color))
            self.list_widget_answer.addItem(item)
        self.list_widget_answer.setVisible(True)

    def _get_note_as_lines(self):
        note_lines = self.edit_notes.toPlainText().splitlines(keepends=False)
        note_lines = (l.strip() for l in note_lines)
        note_lines = [l for l in note_lines if l]
        return note_lines

    def _step_take_notes(self):
        self._toggle_boxes((self.box_meta, self.box_original, self.box_notes))
        self.edit_original.setEnabled(True)
        self.edit_notes.setEnabled(True)
        self.tabbar.setCurrentIndex(0)

    def _step_rewrite(self):
        self._toggle_boxes((self.box_notes, self.box_rewrite))
        self.edit_notes.setDisabled(True)
        self.edit_rewrite.setEnabled(True)
        self.tabbar.setCurrentIndex(1)

    def _step_corrections(self):
        self._toggle_boxes((self.box_original, self.box_corrections))
        self.edit_original.setDisabled(True)
        self.edit_corrections.setEnabled(True)

        if self.tabbar.currentIndex() == 1 and (
            self.edit_corrections.document().isEmpty()
            or self._question_should_overwrite_correction()
        ):
            self.edit_corrections.setPlainText(self.edit_rewrite.toPlainText())

        self.tabbar.setCurrentIndex(2)

    def _step_poetry(self):
        self._toggle_boxes((self.box_corrections, self.box_poetry))
        self.edit_poetry.setEnabled(True)
        self.edit_corrections.setEnabled(False)
        self.tabbar.setCurrentIndex(3)

    def _step_to_prose(self):
        self._toggle_boxes((self.box_poetry, self.box_prose))
        self.edit_poetry.setEnabled(False)
        self.edit_prose.setEnabled(True)
        self.tabbar.setCurrentIndex(4)

    def _step_jumble(self):
        self._toggle_boxes((self.box_jumble,))
        self._on_jumble_clicked()
        self.tabbar.setCurrentIndex(5)

    def _toggle_boxes(self, enabled_boxes):
        for widget in (
            self.box_meta,
            self.box_corrections,
            self.box_jumble,
            self.box_notes,
            self.box_original,
            self.box_poetry,
            self.box_prose,
            self.box_rewrite,
        ):
            if widget in enabled_boxes:
                widget.setVisible(True)
            else:
                widget.setVisible(False)

    def _question_should_overwrite_correction(self):
        return (self._msgbox.exec()) == QMessageBox.Yes
