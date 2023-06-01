import glob
import math
import os
import sys
from collections import namedtuple
from os.path import join

from PyQt5.QtCore import QAbstractTableModel, Qt, QSize, QItemSelectionModel
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QStyledItemDelegate,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QStyle,
)

from exif import Image

# Create a custom namedtuple class to hold our data
preview = namedtuple("preview", "id title image exif_data")

NUMBER_OF_COLUMNS = 4
CELL_PADDING = 20


class PreviewDelegate(QStyledItemDelegate):
    def __init__(self, view):
        super().__init__(view)
        self.view = view
        self.open_windows = []

    def paint(self, painter, option, index):
        print("paint")
        data = index.model().data(index, Qt.DisplayRole)
        if data is None:
            return

        width = option.rect.width() - CELL_PADDING * 2
        height = option.rect.height() - CELL_PADDING * 2

        scaled = data.image.scaled(
            width,
            height,
            aspectRatioMode=Qt.KeepAspectRatio,
        )
        x = int(CELL_PADDING + (width - scaled.width()) / 2)
        y = int(CELL_PADDING + (height - scaled.height()) / 2)

        painter.drawImage(option.rect.x() + x, option.rect.y() + y, scaled)

        if option.state & QStyle.State_Selected:
            painter.setPen(Qt.red)
            painter.drawRect(option.rect)

            exif_data = index.data(Qt.UserRole)
            if exif_data:
                print("open window")
                self.open_new_window(exif_data, index.row(), index.column())
        # else:
        #     self.close_windows()

    def open_new_window(self, exif_data, row, column):
        new_window = QMainWindow()
        new_window.setWindowTitle("Metadata")
        new_window.setGeometry(100, 100, 400, 300)

        label = QLabel(exif_data, new_window)
        label.setGeometry(10, 10, 380, 280)
        label.setWordWrap(True)

        self.open_windows.append(new_window)

        new_window.show()
        self.w = new_window
        # Deselect the image
        model_index = self.view.model().index(row, column)
        self.view.selectionModel().select(model_index, QItemSelectionModel.Deselect)

    # def close_windows(self):
    #     #print("close windows")
    #     for window in self.open_windows:
    #         window.close()
    #     self.open_windows = []

    def sizeHint(self, option, index):
        return QSize(300, 200)


class PreviewModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.previews = []

    def data(self, index, role):
        try:
            data = self.previews[index.row() * 4 + index.column()]
        except IndexError:
            return

        if role == Qt.DisplayRole:
            return data

        if role == Qt.ToolTipRole:
            return data.title

        if role == Qt.UserRole:
            return data.exif_data

    def columnCount(self, index):
        return NUMBER_OF_COLUMNS

    def rowCount(self, index):
        n_items = len(self.previews)
        return math.ceil(n_items / NUMBER_OF_COLUMNS)


class Window2(QMainWindow):
    def __init__(self, directory_path):
        super().__init__()
        self.setFixedSize(1230, 660)
        self.setWindowTitle("PATH: %s" % directory_path)
        self.view = QTableView()
        self.view.horizontalHeader().hide()
        self.view.verticalHeader().hide()
        self.view.setGridStyle(Qt.NoPen)

        delegate = PreviewDelegate(self.view)
        self.view.setItemDelegate(delegate)
        self.model = PreviewModel()
        self.view.setModel(self.model)

        self.setCentralWidget(self.view)

        for n, fn in enumerate(glob.glob(join(directory_path, "*.jpg"))):
            if not os.path.isfile(fn):
                continue

            with open(fn, "rb") as f:
                my_image = Image(f)
                if not my_image.has_exif:
                    continue
                else:
                    image = QImage(fn)
                    exif_data = str(my_image)
                    item = preview(n, fn, image, exif_data)
                    self.model.previews.append(item)
        self.model.layoutChanged.emit()

        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()

    def closeEvent(self, event):
        delegate = self.view.itemDelegate()
        delegate.close_new_window()
        self.view.clearSelection()
        event.accept()

class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "Test 0.1.0v"
        self.top = 100
        self.left = 100
        self.width = 680
        self.height = 500

        self.pushButton = QPushButton("Start", self)
        self.pushButton.move(275, 200)
        self.pushButton.clicked.connect(self.main_window)

        self.start_window()

    def start_window(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def main_window(self):
        directory_path = QFileDialog.getExistingDirectory()
        if directory_path:
            self.w = Window2(directory_path)
            self.w.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
