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
from helpers import Level_Widget

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Important variables for functioning of app
        self.started = False        # Is a level currently in progress?
        self.cam_thread = None      # Placeholder for camera thread
        self.lvl_thread = None      # Placeholder for level thread

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
        self.play_page = Level_Widget()
        self.play_page.SIGNAL.CLOSE.connect(self.close_level)
        

        # Level Select Page
        self.lvl_select_page = QWidget()
        self.label = QLabel()
        self.label.setText('LEVEL SELECT')
        # Back button
        self.back_button1 = QPushButton("Back")
        self.back_button1.clicked.connect(lambda: self.navigate_to(0))
        # adding them all to the layout
        self.lvl_select_lay = QVBoxLayout()
        self.lvl_select_lay.addWidget(self.label)
        self.lvl_select_page.setLayout(self.lvl_select_lay)
        # Level Select Buttons
        for i in range(0, 6):  # Creating 5 buttons with values 1 to 5
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
        self.setWindowState(Qt.WindowFullScreen)

    # Starting a level if safe to do so, assigning the proper variables
    def level_button_clicked(self, value):
        #...
        if not self.started:
            self.started = True
            self.navigate_to(4)
            self.game_loop, self.cam_thread, self.lvl_thread, s, v, o = levels.start_level(self.play_page, value)
        else:
            return 0

    def close_level(self):
        # The custom widget should have already killed its children at this point
        # Safely closing threads
        self.cam_thread.stop()
        self.game_loop.clear()
        self.cam_thread.join()
        self.lvl_thread.join()
        # Freeing up name same (relying on python garbage collector to delete object after this)
        self.cam_thread = None
        self.lvl_thread = None
        self.game_loop = None

        # Navigating to home page
        self.navigate_to(0)
        self.started = False
    
    def navigate_to(self, page):
        self.stacked_main.setCurrentIndex(page)

    def close_app(self):
        self.started = False
        # TODO Add code to save progress here, if needed
        super().close()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()