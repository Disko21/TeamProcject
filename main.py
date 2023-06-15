import sys
import tkinter as tk
from PyQt5.QtWidgets import QDialog,QApplication, QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QFileDialog,QMainWindow,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from os import listdir
from os.path import isfile, join
from exif import Image
import exifread
import os

def openDirectory():
    directory_path = QFileDialog.getExistingDirectory()
    # print all files from directory
    all_files = [directory_path+"/"+ f for f in listdir(directory_path) if isfile(directory_path+"/"+ f)]  
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

        
        layout.addWidget(b2,3,0, alignment=Qt.AlignmentFlag.AlignCenter)
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
        
        tab1=openDirectory()
        #print(tab1)

        button = QPushButton("Zmień obrazek")
        button2 = QPushButton("edycja metadany")
        label = QLabel()
        pixmap = QPixmap(tab1[0])
        scaled_pixmap = pixmap.scaled(600, 400)
        label.setPixmap(scaled_pixmap)
        layout1.addWidget(button, 4,1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(label,4,0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout1.addWidget(button2,4,2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.b=1
        def change_image():
            pixmap2 = QPixmap(tab1[self.b])
            scaled_pixmap2 = pixmap2.scaled(600, 400)
            label.setPixmap(scaled_pixmap2)
            self.b +=1

        def open_new_window():
            new_window = NewWindow2(tab1,self.b)
            new_window.exec_()

        def open_new_window2():
            new_window = NewWindow3(tab1,self.b)
            new_window.exec_()


        button.clicked.connect(lambda: change_image())
        label.mousePressEvent = lambda event: open_new_window()
        button2.clicked.connect(lambda event: open_new_window2())
        self.show()  
class NewWindow2(QDialog):
    def __init__(self, tab1, b):
        super().__init__()
        filename = os.path.basename(tab1[b-1])
        self.setWindowTitle(filename)
        self.tab1 = tab1
        self.b = b
        layout = QGridLayout()
        self.setLayout(layout)
        
        label = QLabel()
        pixmap = QPixmap(self.tab1[b-1])
        scaled_pixmap = pixmap.scaled(600, 400)
        label.setPixmap(scaled_pixmap)

        with open(tab1[b-1], 'rb') as image_file:
            tags = exifread.process_file(image_file, details=False)
            tag_keys = tags.keys()
            print(tags)
         
            # QVBoxLayout for displaying tag names
            tags_layout = QVBoxLayout()
            
            for tag_key in tag_keys:
                tag_label = QLabel(tag_key)
                tags_layout.addWidget(tag_label)

        label1 = QLabel()   
        label1.setText("Tagi:")
        layout.addWidget(label1, 3, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        row = 5
        col = 0
        col_span = 2

        #addWidget TAGKEY
        for tag_key, tag_value in tags.items():
            tag_label = QLabel()
            tag_label.setText(f"{tag_key}: {tag_value}")
            layout.addWidget(tag_label, row, col, 1, col_span, alignment=Qt.AlignmentFlag.AlignLeft)

            col += col_span
            if col >= 4:
                col = 0
                row += 1

        layout.addWidget(label, row+1, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setMinimumSize(600, 400)
class NewWindow3(QDialog):
    def __init__(self, tab1, b):
        super().__init__()

        self.setMinimumSize(600, 400)

        filename = os.path.basename(tab1[b-1])
        self.setWindowTitle(filename)

        self.tab1 = tab1
        self.b = b

        layout = QGridLayout()
        self.setLayout(layout)

        metadana=QLineEdit()
        label = QLabel()
        pixmap = QPixmap(self.tab1[b-1])
        scaled_pixmap = pixmap.scaled(600, 400)
        label.setPixmap(scaled_pixmap)

        with open(tab1[b-1], 'rb') as image_file:
            my_image = Image(image_file)
            tab2=my_image.list_all()
            
        with open(tab1[b-1], 'wb') as new_image_file:
            new_image_file.write(my_image.get_file())
        label2= QLabel()
        i=range(len(tab2))
        for  i in tab2:
            try:
                label2.setText(tab2[i])
            except:
                label2.setText("brak metadanej")
                
        layout.addWidget(label, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label2, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(metadana, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        


if __name__ == '__main__':

    # create pyqt5 app
    app = QApplication(sys.argv)
    # create the instance of our Window
    window = MainWindow()
    window.show()

    # start the app
    sys.exit(app.exec())