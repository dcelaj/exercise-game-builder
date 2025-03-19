from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtGui import Qt
import sys
from time import sleep
import levels

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Has the game started yet? TODO delete when debugging over
        self.started = [False]

        self.setWindowTitle("My App")

        # Main stacked widget to navigate between screens
        self.stacked_main = QStackedWidget()

        # Main menu page
        self.main_menu_page = QWidget()
        self.main_menu_layout = QVBoxLayout()
        self.lvl_butt = QPushButton('Play')
        self.lvl_butt.clicked.connect(lambda: self.navigate_to(1))
        self.op_butt = QPushButton('Options')
        self.op_butt.clicked.connect(lambda: self.navigate_to(2))
        self.gal_butt = QPushButton('Gallery')
        self.gal_butt.clicked.connect(lambda: self.navigate_to(3))
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_app)
        #
        self.main_menu_layout.addWidget(self.lvl_butt)
        self.main_menu_layout.addWidget(self.op_butt)
        self.main_menu_layout.addWidget(self.gal_butt)
        self.main_menu_layout.addWidget(self.quit_button)
        self.main_menu_page.setLayout(self.main_menu_layout)

        # ACTUAL LEVEL PAGE where the called levels.py function can add stuff
        self.play_page = QWidget()

        # Level Select Page
        self.lvl_select_page = QWidget()
        self.label = QLabel()
        self.label.setText('LEVEL SELECT')
        # Back button
        self.back_button1 = QPushButton("Back")
        self.back_button1.clicked.connect(lambda: self.navigate_to(0))
        # Start test button
        self.testt = QPushButton("Start Test")
        self.testt.clicked.connect(self.start_test)
        # adding them all to the layout
        self.lvl_select_lay = QVBoxLayout()
        self.lvl_select_lay.addWidget(self.label)
        self.lvl_select_lay.addWidget(self.testt)
        self.lvl_select_page.setLayout(self.lvl_select_lay)
        # Level Select Buttons
        for i in range(1, 6):  # Creating 5 buttons with values 1 to 5
            level_button = QPushButton(f"Level {i}")
            level_button.clicked.connect(lambda checked, x=i: self.level_button_clicked(x))
            self.lvl_select_lay.addWidget(level_button)
        # Add back button    
        self.lvl_select_lay.addWidget(self.back_button1)

        # Options page
        self.op_page = QWidget()
        self.op_lay = QVBoxLayout()
        self.op_page.setLayout(self.op_lay)
        self.back_button2 = QPushButton("Back")
        self.back_button2.clicked.connect(lambda: self.navigate_to(0))
        self.op_lay.addWidget(self.back_button2)

        # Gallery page
        self.gal_page = QWidget()
        self.gal_lay = QVBoxLayout()
        self.gal_page.setLayout(self.gal_lay)
        self.back_button3 = QPushButton("Back")
        self.back_button3.clicked.connect(lambda: self.navigate_to(0))
        self.gal_lay.addWidget(self.back_button3)

        # ADD ALL THE PAGES TO STACKED WIDGET
        self.stacked_main.addWidget(self.main_menu_page)
        self.stacked_main.addWidget(self.lvl_select_page)
        self.stacked_main.addWidget(self.op_page)
        self.stacked_main.addWidget(self.gal_page)
        self.stacked_main.addWidget(self.play_page)

        # Set the central widget of the Window.
        self.setCentralWidget(self.stacked_main)

    #...
    def level_button_clicked(self, value):
        self.label.setText(f"Loading Level {value}")
        QApplication.processEvents()

        #...
        if not self.started[0]:
            #self.started = True # TODO: re-enable and find a way to make it false again when threads exit
            levels.start_level(value)
        else:
            print("already started bosss")
        
        #...
        self.label.setText(f"Done!")

    def start_test(self):
        if not self.started[0]:
            self.feed = levels.level1()
            self.layout.addWidget(self.feed)
            self.started[0] = True
        else: 
            self.started[0] = False
            sleep(5)
    
    def navigate_to(self, page):
        if page == 4:
            # This is only done for the screen where the gameplay takes place, sets fullscreen
            self.setWindowState(Qt.WindowFullScreen)
        self.stacked_main.setCurrentIndex(page)

    def close_app(self):
        self.started[0] = False
        sleep(0.5)
        super().close()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()