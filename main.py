import sys
from PyQt5 import QtWidgets
from Search import MySearch

app = QtWidgets.QApplication(sys.argv)
mysearch = MySearch()
mysearch.start()
sys.exit(app.exec_())