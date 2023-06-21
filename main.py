import sys
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QFileDialog
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QPixmap
from os import listdir
from os.path import isfile
from exif import Image, DATETIME_STR_FORMAT
import exifread
import os
from datetime import datetime


def openDirectory():
    directory_path = QFileDialog.getExistingDirectory()
    # print all files from directory
    all_files = [directory_path + "/" + f for f in listdir(directory_path) if
                 isfile(directory_path + "/" + f) and f.lower().endswith(('.jpeg', '.jpg'))]
    return all_files


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Edytor zdjęć')

        # set the grid layout
        layout = QGridLayout()
        self.setFixedSize(300, 220)
        self.setLayout(layout)

        # button
        b2 = QPushButton('Start')

        layout.addWidget(b2, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # button onclick event
        b2.clicked.connect(self.show_new_window)

    def show_new_window(self):
        new_window = NewWindow()
        new_window.exec_()


class NewWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nowe okno")
        layout1 = QGridLayout()
        self.setLayout(layout1)

        tab1 = openDirectory()
        print(tab1)

        button1 = QPushButton("cofnij obrazek")
        button2 = QPushButton("edycja metadany")
        button3 = QPushButton("następny obrazek")

        label = QLabel()
        pixmap = QPixmap(tab1[0])
        scaled_pixmap = pixmap.scaled(600, 400)
        label.setPixmap(scaled_pixmap)
        layout1.addWidget(button1, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(label, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(button2, 4, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(button3, 4, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        self.b = 1

        def next_image():
            pixmap2 = QPixmap(tab1[self.b])
            scaled_pixmap2 = pixmap2.scaled(600, 400)
            label.setPixmap(scaled_pixmap2)
            print(self.b)
            self.b += 1
            if self.b == len(tab1):
                self.b = 0

        def previous_image():
            pixmap2 = QPixmap(tab1[self.b])
            scaled_pixmap2 = pixmap2.scaled(600, 400)
            label.setPixmap(scaled_pixmap2)
            print(self.b)
            if self.b == 0:
                self.b = len(tab1)
            self.b -= 1

        def open_new_window():
            new_window = NewWindow2(tab1, self.b)
            new_window.exec_()

        def open_new_window2():
            new_window = NewWindow3(tab1, self.b)
            new_window.exec_()

        button1.clicked.connect(previous_image)
        label.mousePressEvent = open_new_window
        button2.clicked.connect(open_new_window2)
        button3.clicked.connect(next_image)
        self.show()


class NewWindow2(QDialog):
    def __init__(self, tab1, b):
        super().__init__()
        filename = os.path.basename(tab1[b - 1])
        self.setWindowTitle(filename)
        self.tab1 = tab1
        self.b = b
        layout = QGridLayout()
        self.setLayout(layout)

        label = QLabel()
        pixmap = QPixmap(self.tab1[b - 1])
        scaled_pixmap = pixmap.scaled(600, 400)
        label.setPixmap(scaled_pixmap)

        with open(tab1[b - 1], 'rb') as image_file:
            tags = exifread.process_file(image_file, details=False)
            tags.keys()
            print(tags)

        label1 = QLabel()
        label1.setText("Tagi:")
        layout.addWidget(label1, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        row = 5
        col = 0
        col_span = 2

        # addWidget TAGKEY
        for tag_key, tag_value in tags.items():
            tag_label = QLabel()
            tag_label.setText(f"{tag_key}: {tag_value}")
            layout.addWidget(tag_label, row, col, 1, col_span, alignment=Qt.AlignmentFlag.AlignLeft)

            col += col_span
            if col >= 4:
                col = 0
                row += 1

        layout.addWidget(label, row + 1, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setMinimumSize(600, 400)


class NewWindow3(QDialog):
    def __init__(self, tab1, b):
        super().__init__()

        self.setMinimumSize(600, 400)

        filename = os.path.basename(tab1[b - 1])
        self.setWindowTitle(filename)

        self.tab1 = tab1

        layout = QGridLayout()
        self.setLayout(layout)

        with open(tab1[b - 1], 'rb') as image_file:
            my_image = Image(image_file)
            my_image.list_all()

        def zast():
            model = metadana.text()

            nazwa = metadana2.text()

            gps = metadana3.text()
            gps = gps.split(',')

            gps2 = metadana6.text()
            gps2 = gps2.split(',')

            data = metadana4.text()
            data = data.split('.')
            data_wykonania = datetime(year=int(data[0]), month=int(data[1]), day=int(data[2]), hour=int(data[3]),
                                      minute=int(data[4]), second=int(data[5]))
            my_image.datetime_original = data_wykonania.strftime(DATETIME_STR_FORMAT)

            data2 = metadana5.text()
            data2 = data2.split('.')
            data_s = datetime(year=int(data2[0]), month=int(data2[1]), day=int(data2[2]), hour=int(data2[3]),
                              minute=int(data2[4]), second=int(data2[5]))
            my_image.datetime_digitized = data_s.strftime(DATETIME_STR_FORMAT)

            print(f"{gps}+{nazwa}+{model}+{data_wykonania}")
            my_image.gps_longitude = (float(gps2[0]), float(gps2[1]), float(gps2[2]))
            my_image.gps_latitude = (float(gps[0]), float(gps[1]), float(gps[2]))
            my_image.model = model

            with open(nazwa, 'wb') as new_image_file:
                new_image_file.write(my_image.get_file())


        current_datetime = QDateTime.currentDateTime().toString("yyyy.MM.dd.hh.mm.ss")

        metadana = QLineEdit()
        label = QLabel()
        metadana.setText(" ")
        label.setText("Model_urządzenia")

        metadana2 = QLineEdit()
        label2 = QLabel()
        metadana2.setText("new_"+filename)
        label2.setText("Nazwa pliku")

        metadana3 = QLineEdit()
        label3 = QLabel()
        metadana3.setText("0, 0, 0, 0")
        label3.setText("gps_latitude(-.-,-.-,-.-)")

        metadana4 = QLineEdit()
        metadana4.setText(current_datetime)
        label4 = QLabel()
        label4.setText("Data_Wykonania(yyyy.mm.dd.hh.min.s)")

        metadana5 = QLineEdit()
        metadana5.setText(current_datetime)
        label5 = QLabel()
        label5.setText("Data_S(yyyy.mm.dd.hh.min.s)")

        metadana6 = QLineEdit()
        metadana6.setText("0, 0, 0, 0")
        label6 = QLabel()
        label6.setText("gps_longitude(-.-,-.-,-.-)")

        zastosuj = QPushButton("Zastosuj")
        zastosuj.clicked.connect(zast)

        zastosuj.clicked.connect(zast)
        layout.addWidget(label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label2, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana2, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label3, 3, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana3, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label4, 4, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana4, 4, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label5, 5, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana5, 5, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label6, 6, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana6, 6, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(zastosuj, 7, 1, alignment=Qt.AlignmentFlag.AlignCenter)


if __name__ == '__main__':
    # create pyqt5 app
    app = QApplication(sys.argv)
    # create the instance of our Window
    window = MainWindow()
    window.show()

    # start the app
    sys.exit(app.exec())
