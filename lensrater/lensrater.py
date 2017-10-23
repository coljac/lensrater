#!env python3

import os
import sys
# import pandas as pd
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMainWindow, QDesktopWidget
try:
    from . import mainwindow
except ImportError:
    try: 
        import mainwindow
    except ModuleNotFoundError:
        pass

from collections import defaultdict


def find_files(dirname, match=None):
    result = []
    for root, dirs, files in os.walk(dirname):
        for file_ in files:
            if match is None or match in file_:
                result.append(file_)
    return result


class LensRater(QMainWindow, mainwindow.Ui_MainWindow):
    """ A hacked-together gui for rating lens images.
    TODO:
        Side-by-side for subtractions or single band images
        Expand image - zoom out
        Zoom in further
        Review choices made
        Produce output montages
        Access images remotely
    """

    colour_codes = [Qt.black, QColor(27, 76, 198), QColor(234, 224, 23), QColor(198, 13, 13), Qt.gray]
    categories = ["", "Maybe", "Probably", "Definitely"]

    def __init__(self, image_dir):
        super(LensRater, self).__init__()
        self.setupUi(self)

        self.next_button.clicked.connect(self.nextImage)
        self.prev_button.clicked.connect(self.prevImage)

        self.image_dir = image_dir
        self.image_files = find_files(image_dir, match=".png")
        if len(self.image_files) == 0:
            print("No image files found.")
            sys.exit(0)
        self.image_index = 0
        self.current_image = None
        self.progress_bar.setMaximum(len(self.image_files))
        self.scorefile = self.image_dir + "/scores.csv"
        self.scores = defaultdict(lambda: -1)
        # self.setChildrenFocusPolicy(QtCore.Qt.NoFocus)
        QtWidgets.qApp.installEventFilter(self)

        self.radios = [self.radio_0, self.radio_1, self.radio_2, self.radio_3]
        for i in range(4):
            self.radios[i].toggled.connect(self.radio_score)

        self.set_username_button.clicked.connect(self.update_username)
        self.username_edit.returnPressed.connect(self.set_username)
        self.jump_box.returnPressed.connect(self.jumped_to)
        self.actionSave_and_Quit.triggered.connect(self.close)

        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.set_label.setText(os.path.abspath(image_dir).split("/")[-1])
        self.username = os.environ.get("USER", "nobody")
        self.load()
        self.username_edit.setText(self.username)
        self.go_to_last()
        # self.goto_image(0)

    def set_colour_code(self, colour):
        p = self.colour_label.palette()
        p.setColor(self.backgroundRole(), colour)
        self.colour_label.setPalette(p)

    def setChildrenFocusPolicy(self, policy):
        def recursiveSetChildFocusPolicy(parentQWidget):
            for childQWidget in parentQWidget.findChildren(QWidget):
                if childQWidget == self.username_edit:
                    continue
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)

        recursiveSetChildFocusPolicy(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Left or event.key(
            ) == QtCore.Qt.Key_Right:
                self.keyPressEvent(event)
                return True
        return super(LensRater, self).eventFilter(source, event)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_J:
            self.nextImage()
        elif e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_K:
            self.prevImage()
        elif e.key() == QtCore.Qt.Key_End:
            self.goto_image(len(self.image_files) - 1)
        elif e.key() == QtCore.Qt.Key_Home:
            self.goto_image(0)
        elif e.key() == QtCore.Qt.Key_PageUp:
            self.goto_image(max(self.image_index - 10, 0))
        elif e.key() == QtCore.Qt.Key_PageDown:
            self.goto_image(
                min(self.image_index + 10, len(self.image_files) - 1))
        elif e.key() == QtCore.Qt.Key_Space:
            self.up_score()
        elif e.key() == QtCore.Qt.Key_0 or e.key() == QtCore.Qt.Key_QuoteLeft:
            self.score_image(0)
        elif e.key() == QtCore.Qt.Key_1:
            self.score_image(1)
        elif e.key() == QtCore.Qt.Key_2:
            self.score_image(2)
        elif e.key() == QtCore.Qt.Key_3:
            self.score_image(3)
        # elif e.key() == QtCore.Qt.Key_Right:
        # pass
        # elif e.key() == QtCore.Qt.Key_Right:
        # pass
        # elif e.key() == QtCore.Qt.Key_Right:
        # pass
        elif e.key() == QtCore.Qt.Key_Return:
            pass
            # self.close()

    def nextImage(self):
        if self.image_index < len(self.image_files) - 1:
            self.image_index += 1
            self.goto_image(self.image_index)

    def prevImage(self):
        if self.image_index > 0:
            self.image_index -= 1
            self.goto_image(self.image_index)

    def goto_image(self, index):
        self.image_index = index
        self.current_image = self.image_files[index]
        self.set_display_image(self.image_files[index])
        self.position_label.setText(str(index) +": " + self.current_image)
        self.progress_bar.setValue(index + 1)
        current_score = self.scores[self.current_image]
        self.set_colour_code(LensRater.colour_codes[current_score])
        self.toggle_radio(current_score)

        if current_score < 0:  # Implicitly score when seen
            self.score_image(0)

    def toggle_radio(self, score):
        for i in range(4):
            self.radios[i].setChecked(i == score)

    def set_display_image(self, impath):
        image_profile = QtGui.QImage(self.image_dir + "/" + impath)
        # image_profile = image_profile.scaled(200, 200, \
                    # aspectRatioMode=QtCore.Qt.KeepAspectRatio, \
                    # transformMode=QtCore.Qt.SmoothTransformation)
        self.image_label.setScaledContents(True)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(image_profile))

    def up_score(self):
        current_score = self.scores[self.current_image]
        newscore = current_score + 1
        if newscore > 3:
            newscore = 0
        self.score_image(newscore)

    def go_to_last(self):
        for i, f in enumerate(self.image_files):
            if self.scores[f] < 0:
                self.goto_image(i)
                break
            
    def radio_score(self):
        for i in range(4):
            if self.radios[i].isChecked():
                self.score_image(i)
                break

    def score_image(self, score):
        self.scores[self.current_image] = score
        self.set_colour_code(LensRater.colour_codes[score])
        self.toggle_radio(score)
        self.colour_label.setText(LensRater.categories[score])

    def load(self):
        if os.path.isfile(self.scorefile):
            with open(self.scorefile, "r") as f:
                lines = [s.split(",") for s in f.readlines()]
            self.username = lines[1][0]
            for line in lines[1:]:
                self.scores[line[1]] = int(line[2])

    def jumped_to(self):
        # self.jump_box.setEnabled(False)
        self.setFocus()
        goto = self.jump_box.text()
        try:
            goto = int(goto)
            self.goto_image(goto)
        except ValueError:
            pass
        self.jump_box.setText("")

    def update_username(self):
        self.username_edit.setEnabled(True)
        self.username_edit.setText("")
        self.username_edit.setFocus()

    def set_username(self):
        self.set_username_(self.username_edit.text())
        self.username_edit.setEnabled(False)
        self.username_edit.setFocus()

    def set_username_(self, username):
        self.username = username

    def review_scores(self):
        pass

    def save(self):
        with open(self.scorefile, "w") as f:
            f.write("username,image,score\n")
            for file_ in self.image_files:
                f.write("%s,%s,%d\n" % (self.username, file_.split("/")[-1],\
                        self.scores[file_]))

    def close(self):
        self.save()
        super(LensRater, self).close()


def main():
    app = QApplication(sys.argv)
    iconloc = "/".join(__file__.split("/")[0:-1]) + '/icon.png'
    print(iconloc)
    app.setWindowIcon(QIcon(iconloc))
    imgdir = "."
    if len(sys.argv) > 1:
        imgdir = sys.argv[1]
    window = LensRater(imgdir)
    app.aboutToQuit.connect(window.save)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
