

import sys
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QSizePolicy
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor
from PyQt5 import QtWidgets

class Button(QPushButton):
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.RightButton:
            return

        # write the relative cursor position to mime data
        mimeData = QMimeData()
        # simple string with 'x,y'
        mimeData.setText('%d,%d' % (e.x(), e.y()))

        # let's make it fancy. we'll show a "ghost" of the button as we drag
        # grab the button to a pixmap
        pixmap = QWidget.grab(self)

        # below makes the pixmap half transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()

        # make a QDrag
        drag = QDrag(self)
        # put our MimeData
        drag.setMimeData(mimeData)
        # set its Pixmap
        drag.setPixmap(pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(e.pos())

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        if drag.exec_(Qt.CopyAction | Qt.MoveAction) == Qt.MoveAction:
            print('moved')
        else:
            print('copied')


    def mousePressEvent(self, e):
        QPushButton.mousePressEvent(self, e)
        if e.button() == Qt.LeftButton:
            print('press')



class DropWidget(QWidget):
    def __init__(self,plotWindow,layout):
        super(DropWidget, self).__init__()
        self.setAcceptDrops(True)
        self.plotWindow = plotWindow
        self.layout = layout
    def dragEnterEvent(self, e):
        e.accept()


    def dropEvent(self, e):
        # get the relative position from the mime data
        mime = e.mimeData().text()
        x, y = map(int, mime.split(','))

        if e.keyboardModifiers() & Qt.ShiftModifier:
            '''
            # copy
            # so create a new button
            button = Button('Button', self)
            # move it to the position adjusted with the cursor position at drag
            button.move(e.pos()-QPoint(x, y))
            # show it
            button.show()
            # store it
            self.buttons.append(button)
            # set the drop action as Copy
            e.setDropAction(Qt.CopyAction)
            '''

        else:
            # move
            # so move the dragged button (i.e. event.source())
            e.source().move(e.pos()-QPoint(x, y))
            # set the drop action as Move
            e.setDropAction(Qt.MoveAction)
            self.layout.addWidget(e.source())
            self.plotWindow.onLayoutChange()
        # tell the QDrag we accepted it
        e.accept()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DropWidget()
    ex.show()
    app.exec_()
