import threading, time
from package import interface
from PyQt5 import QtWidgets, QtCore, QtGui
import lastversion
import depth

class MySearch(QtWidgets.QWidget):
    def __init__(self):
        super(MySearch, self).__init__()
        self.face = interface.Ui_Search()
        self.face.setupUi(self)
        self.algorithms = ['深度优化', '全局优化']
        self.labels = ['编号和深度：', '编号和损失值：']
        self.nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
        self.frame_rates = ['0.5', '1', '2', '5', '10', '50', '100', '200']
        self.initial_state = ''
        self.target = ''
        self.algorithm = ''
        self.efficiency = ''
        self.efficiency_num = 4 # 效率保留4位小数
        self.results = ''
        '''
        记录所有步骤，一个元素记录一个步骤，每个元素都是list，由open表（list）、close表（list）、
        当前节点（list，包含节点的值，编号，损失值），父节点（list），扩展节点（list），兄弟节点（list）
        组成。
        '''
        self.current_result = 0  # 记录当前步骤在self.results中的位置（通过索引记录）
        self.results_total = 0
        self.current_rate = 0
        self.depth_max = ""
        self.depth_maxs = ['4', '6', '8', '10', '12']
        self.heuristic = ""
        self.heuristics = ['第一种', '第二种']
        self.play_time = False
        self.play_thread_quit = True
        # 值为False表示当前有子线程正在运行，为True表示当前无子线程运行，可创建新的子线程
        self.font1 = QtGui.QFont()
        self.font2 = QtGui.QFont()
        self.set_font1(self.font1)
        self.set_font2(self.font2)
        self.interface_initialization()

    def set_font1(self, font):
        font.setFamily('微软雅黑')
        font.setBold(True)
        font.setPointSize(15)
        font.setWeight(75)
    def set_font2(self, font):
        font.setFamily('微软雅黑')
        font.setBold(True)
        font.setPointSize(13)
        font.setWeight(75)
    def interface_initialization(self):
        self.center()  # 窗口控件尺寸太大会不在屏幕中心，所以要自定义窗口位置
        self.view_btn_forbid()
        self.set_btn_font()
        self.bindbutton()
        self.face.lineEdit_initial_state.setPlaceholderText("请输入数字0~8")
        self.face.lineEdit_target.setPlaceholderText("请输入数字0~8")
        self.face.comboBox_dm.addItems(self.depth_maxs)
        self.face.comboBox_dm.setCurrentIndex(-1)
        self.face.label_dm.setVisible(False)
        self.face.comboBox_dm.setVisible(False)
        self.face.comboBox_heuristic.addItems(self.heuristics)
        self.face.comboBox_heuristic.setCurrentIndex(-1)
        self.face.label_heuristic.setVisible(False)
        self.face.comboBox_heuristic.setVisible(False)
        self.face.comboBox_algorithm.addItems(self.algorithms)
        self.face.comboBox_algorithm.setCurrentIndex(-1)
        self.face.comboBox_frame_rate.addItems(self.frame_rates)
        self.face.comboBox_frame_rate.setCurrentIndex(-1)
        self.face.lineEdit_open.setFocusPolicy(QtCore.Qt.NoFocus)
        self.face.lineEdit_close.setFocusPolicy(QtCore.Qt.NoFocus)
        # 设置不可获得焦点，从而不可编辑，又能查看完整的显示文本。

    def center(self):
        qr = self.frameGeometry()
        # frameGeometry() 方法允许我们创建一个无形矩形并根据主窗口的宽高设置自身的宽度与高度
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        # 计算出显示器的屏幕分辨率。根据得到的分辨率得到屏幕的中心点。
        qr.moveCenter(cp)
        # 移动矩形的中心到屏幕的中心点(cp)，矩形的尺寸是不变的
        self.move(qr.topLeft())
        # 移动应用程序窗口的左上角到qr矩形的左上角，从而使应用程序窗口显示在屏幕的中心。

    def input_forbid(self):
        self.face.lineEdit_initial_state.setEnabled(False)
        self.face.lineEdit_target.setEnabled(False)
        self.face.comboBox_algorithm.setEnabled(False)
        self.face.comboBox_dm.setEnabled(False)
        self.face.comboBox_heuristic.setEnabled(False)

    def input_restore(self):
        self.face.lineEdit_initial_state.setEnabled(True)
        self.face.lineEdit_target.setEnabled(True)
        self.face.comboBox_algorithm.setEnabled(True)
        self.face.comboBox_dm.setEnabled(True)
        self.face.comboBox_heuristic.setEnabled(True)

    def view_btn_forbid(self):
        self.face.btn_previous_step.setEnabled(False)
        self.face.btn_next_step.setEnabled(False)
        self.face.btn_first_step.setEnabled(False)
        self.face.btn_last_step.setEnabled(False)
        self.face.btn_play.setEnabled(False)
        self.face.btn_formatting.setEnabled(False)
        self.face.comboBox_frame_rate.setEnabled(False)
    def view_btn_restore(self):
        self.face.btn_previous_step.setEnabled(True)
        self.face.btn_next_step.setEnabled(True)
        self.face.btn_first_step.setEnabled(True)
        self.face.btn_last_step.setEnabled(True)
        self.face.btn_play.setEnabled(True)
        self.face.btn_formatting.setEnabled(True)
        self.face.comboBox_frame_rate.setEnabled(True)

    def bindbutton(self):
        self.face.btn_start.clicked.connect(self.start_presentation)
        self.face.btn_previous_step.clicked.connect(self.previous_step)
        self.face.btn_next_step.clicked.connect(self.next_step)
        self.face.btn_first_step.clicked.connect(self.first_step)
        self.face.btn_last_step.clicked.connect(self.last_step)
        self.face.btn_formatting.clicked.connect(self.formatting)
        self.face.btn_play.clicked.connect(self.play)
        self.face.comboBox_algorithm.currentIndexChanged.connect(self.attr_display)
        self.face.comboBox_frame_rate.currentIndexChanged.connect(self.rate_change)

    def set_btn_font(self):
        self.face.btn_show_c_1.setFont(self.font1)
        self.face.btn_show_c_2.setFont(self.font1)
        self.face.btn_show_c_3.setFont(self.font1)
        self.face.btn_show_c_4.setFont(self.font1)
        self.face.btn_show_c_5.setFont(self.font1)
        self.face.btn_show_c_6.setFont(self.font1)
        self.face.btn_show_c_7.setFont(self.font1)
        self.face.btn_show_c_8.setFont(self.font1)
        self.face.btn_show_c_9.setFont(self.font1)
        self.face.btn_show_c_num.setFont(self.font1)
        self.face.btn_show_c_loss.setFont(self.font1)
        self.face.btn_show_f_1.setFont(self.font2)
        self.face.btn_show_f_2.setFont(self.font2)
        self.face.btn_show_f_3.setFont(self.font2)
        self.face.btn_show_f_4.setFont(self.font2)
        self.face.btn_show_f_5.setFont(self.font2)
        self.face.btn_show_f_6.setFont(self.font2)
        self.face.btn_show_f_7.setFont(self.font2)
        self.face.btn_show_f_8.setFont(self.font2)
        self.face.btn_show_f_9.setFont(self.font2)
        self.face.btn_show_f_num.setFont(self.font2)
        self.face.btn_show_f_loss.setFont(self.font2)
        self.face.btn_show_e_1_1.setFont(self.font2)
        self.face.btn_show_e_1_2.setFont(self.font2)
        self.face.btn_show_e_1_3.setFont(self.font2)
        self.face.btn_show_e_1_4.setFont(self.font2)
        self.face.btn_show_e_1_5.setFont(self.font2)
        self.face.btn_show_e_1_6.setFont(self.font2)
        self.face.btn_show_e_1_7.setFont(self.font2)
        self.face.btn_show_e_1_8.setFont(self.font2)
        self.face.btn_show_e_1_9.setFont(self.font2)
        self.face.btn_show_e_1_num.setFont(self.font2)
        self.face.btn_show_e_1_loss.setFont(self.font2)
        self.face.btn_show_e_2_1.setFont(self.font2)
        self.face.btn_show_e_2_2.setFont(self.font2)
        self.face.btn_show_e_2_3.setFont(self.font2)
        self.face.btn_show_e_2_4.setFont(self.font2)
        self.face.btn_show_e_2_5.setFont(self.font2)
        self.face.btn_show_e_2_6.setFont(self.font2)
        self.face.btn_show_e_2_7.setFont(self.font2)
        self.face.btn_show_e_2_8.setFont(self.font2)
        self.face.btn_show_e_2_9.setFont(self.font2)
        self.face.btn_show_e_2_num.setFont(self.font2)
        self.face.btn_show_e_2_loss.setFont(self.font2)
        self.face.btn_show_e_3_1.setFont(self.font2)
        self.face.btn_show_e_3_2.setFont(self.font2)
        self.face.btn_show_e_3_3.setFont(self.font2)
        self.face.btn_show_e_3_4.setFont(self.font2)
        self.face.btn_show_e_3_5.setFont(self.font2)
        self.face.btn_show_e_3_6.setFont(self.font2)
        self.face.btn_show_e_3_7.setFont(self.font2)
        self.face.btn_show_e_3_8.setFont(self.font2)
        self.face.btn_show_e_3_9.setFont(self.font2)
        self.face.btn_show_e_3_num.setFont(self.font2)
        self.face.btn_show_e_3_loss.setFont(self.font2)
        self.face.btn_show_e_4_1.setFont(self.font2)
        self.face.btn_show_e_4_2.setFont(self.font2)
        self.face.btn_show_e_4_3.setFont(self.font2)
        self.face.btn_show_e_4_4.setFont(self.font2)
        self.face.btn_show_e_4_5.setFont(self.font2)
        self.face.btn_show_e_4_6.setFont(self.font2)
        self.face.btn_show_e_4_7.setFont(self.font2)
        self.face.btn_show_e_4_8.setFont(self.font2)
        self.face.btn_show_e_4_9.setFont(self.font2)
        self.face.btn_show_e_4_num.setFont(self.font2)
        self.face.btn_show_e_4_loss.setFont(self.font2)
        self.face.btn_show_b_1_1.setFont(self.font2)
        self.face.btn_show_b_1_2.setFont(self.font2)
        self.face.btn_show_b_1_3.setFont(self.font2)
        self.face.btn_show_b_1_4.setFont(self.font2)
        self.face.btn_show_b_1_5.setFont(self.font2)
        self.face.btn_show_b_1_6.setFont(self.font2)
        self.face.btn_show_b_1_7.setFont(self.font2)
        self.face.btn_show_b_1_8.setFont(self.font2)
        self.face.btn_show_b_1_9.setFont(self.font2)
        self.face.btn_show_b_1_num.setFont(self.font2)
        self.face.btn_show_b_1_loss.setFont(self.font2)
        self.face.btn_show_b_2_1.setFont(self.font2)
        self.face.btn_show_b_2_2.setFont(self.font2)
        self.face.btn_show_b_2_3.setFont(self.font2)
        self.face.btn_show_b_2_4.setFont(self.font2)
        self.face.btn_show_b_2_5.setFont(self.font2)
        self.face.btn_show_b_2_6.setFont(self.font2)
        self.face.btn_show_b_2_7.setFont(self.font2)
        self.face.btn_show_b_2_8.setFont(self.font2)
        self.face.btn_show_b_2_9.setFont(self.font2)
        self.face.btn_show_b_2_num.setFont(self.font2)
        self.face.btn_show_b_2_loss.setFont(self.font2)
        self.face.btn_show_b_3_1.setFont(self.font2)
        self.face.btn_show_b_3_2.setFont(self.font2)
        self.face.btn_show_b_3_3.setFont(self.font2)
        self.face.btn_show_b_3_4.setFont(self.font2)
        self.face.btn_show_b_3_5.setFont(self.font2)
        self.face.btn_show_b_3_6.setFont(self.font2)
        self.face.btn_show_b_3_7.setFont(self.font2)
        self.face.btn_show_b_3_8.setFont(self.font2)
        self.face.btn_show_b_3_9.setFont(self.font2)
        self.face.btn_show_b_3_num.setFont(self.font2)
        self.face.btn_show_b_3_loss.setFont(self.font2)

    def attr_display(self):
        algorithm = self.face.comboBox_algorithm.currentText()
        if algorithm == self.algorithms[0]:
            self.face.label_dm.setVisible(True)
            self.face.comboBox_dm.setVisible(True)
            self.face.label_heuristic.setVisible(False)
            self.face.comboBox_heuristic.setVisible(False)
        elif algorithm == self.algorithms[1]:
            self.face.label_dm.setVisible(False)
            self.face.comboBox_dm.setVisible(False)
            self.face.label_heuristic.setVisible(True)
            self.face.comboBox_heuristic.setVisible(True)
        else:
            self.face.label_dm.setVisible(False)
            self.face.comboBox_dm.setVisible(False)
            self.face.label_heuristic.setVisible(False)
            self.face.comboBox_heuristic.setVisible(False)

    def start_presentation(self):  # 点击 开始演示 按钮调用
        initial_state = self.face.lineEdit_initial_state.text().strip()
        target = self.face.lineEdit_target.text().strip()
        algorithm = self.face.comboBox_algorithm.currentText()
        depth_max = self.face.comboBox_dm.currentText()
        heuristic = self.face.comboBox_heuristic.currentText()
        if not initial_state:
            self.reply("请输入初始状态")
            return
        if not target:
            self.reply("请输入目标状态")
            return
        if not algorithm:
            self.reply("请选择算法")
            return
        if algorithm == self.algorithms[0] and not depth_max:
            self.reply("请选择最大深度")
            return
        if algorithm == self.algorithms[1] and not heuristic:
            self.reply("请选择启发式搜索函数")
            return
        if not self.check(initial_state):
            self.reply("请输入规范的初始状态")
            return
        if not self.check(target):
            self.reply("请输入规范的目标状态")
            return
        if initial_state == target:
            self.reply('初始状态与目标状态不能相同')
            return
        self.initial_state = initial_state
        self.target = target
        self.algorithm = algorithm
        self.depth_max = depth_max
        self.heuristic = heuristic
        self.judge()

    def reply(self, content):  # 弹出消息框所用
        reply = QtWidgets.QMessageBox()
        reply.setWindowTitle('出错')
        reply.setText(content)
        reply.addButton(QtWidgets.QPushButton('关闭'), QtWidgets.QMessageBox.YesRole)
        reply.exec_()

    def check(self, content):  # 检查初始状态和目标状态调用
        content = list(content)
        for item in content:
            if item not in self.nums:
                return 0
        if sorted(content) != self.nums:
            return 0
        return 1

    def judge(self):  # 判断用什么算法等
        if self.algorithm == self.algorithms[0]:
            data = depth.process(self.initial_state, self.target, int(self.depth_max))
            if not data:
                self.reply('目标布局不可达')
                return
            self.efficiency = '无'
            self.results = data
            self.results_total = len(self.results)
            self.current_result = 0
            self.label_set(0)
        if self.algorithm == self.algorithms[1]:
            self.heuristic = 1 if self.heuristic == "第一种" else 2
            data = lastversion.main(self.initial_state, self.target, self.heuristic)
            if not data:
                self.reply('目标布局不可达')
                return
            self.efficiency = round(data[0], self.efficiency_num)
            self.results = data[1]
            self.results_total = len(self.results)
            self.current_result = 0
            self.label_set(1)
        self.input_forbid()
        self.view_btn_restore()
        self.face.btn_previous_step.setEnabled(False)
        self.face.btn_start.setEnabled(False)
        self.state_show()

    def state_show(self):  # 显示状态
        result_displayed = self.results[self.current_result]
        open_table = result_displayed[0]
        close_table = result_displayed[1]
        current_node = result_displayed[2]
        father_node = result_displayed[3]
        expanding_nodes = result_displayed[4]
        brother_nodes = result_displayed[5]
        self.open_show(open_table)
        self.close_show(close_table)
        self.current_node_show(current_node)
        self.father_node_show(father_node)
        self.expanding_nodes_show(expanding_nodes)
        self.brother_nodes_show(brother_nodes)

    def open_show(self, open_table):
        open_table = ["(" + str(item) + ')' for item in open_table]
        open_table = ','.join(open_table)
        self.face.lineEdit_open.clear()
        self.face.lineEdit_open.setText(open_table)

    def close_show(self, close_table):
        close_table = ["(" + str(item) + ')' for item in close_table]
        close_table = ','.join(close_table)
        self.face.lineEdit_close.clear()
        self.face.lineEdit_close.setText(close_table)

    def label_set(self, label_index):
        self.face.label_c_num.setText(self.labels[label_index])
        self.face.label_f_num.setText(self.labels[label_index])
        self.face.label_b_num.setText(self.labels[label_index])
        self.face.label_e_num.setText(self.labels[label_index])

    def current_node_show(self, node):
        self.face.btn_show_c_1.setText(node[0][0])
        self.face.btn_show_c_2.setText(node[0][1])
        self.face.btn_show_c_3.setText(node[0][2])
        self.face.btn_show_c_4.setText(node[0][3])
        self.face.btn_show_c_5.setText(node[0][4])
        self.face.btn_show_c_6.setText(node[0][5])
        self.face.btn_show_c_7.setText(node[0][6])
        self.face.btn_show_c_8.setText(node[0][7])
        self.face.btn_show_c_9.setText(node[0][8])
        self.face.btn_show_c_num.setText(str(node[1]))
        self.face.btn_show_c_loss.setText(str(node[2]))

    def father_node_show(self, node):
        try:
            self.face.btn_show_f_1.setText(node[0][0])
            self.face.btn_show_f_2.setText(node[0][1])
            self.face.btn_show_f_3.setText(node[0][2])
            self.face.btn_show_f_4.setText(node[0][3])
            self.face.btn_show_f_5.setText(node[0][4])
            self.face.btn_show_f_6.setText(node[0][5])
            self.face.btn_show_f_7.setText(node[0][6])
            self.face.btn_show_f_8.setText(node[0][7])
            self.face.btn_show_f_9.setText(node[0][8])
            self.face.btn_show_f_num.setText(str(node[1]))
            self.face.btn_show_f_loss.setText(str(node[2]))
        except:
            self.face.btn_show_f_1.setText("")
            self.face.btn_show_f_2.setText("")
            self.face.btn_show_f_3.setText("")
            self.face.btn_show_f_4.setText("")
            self.face.btn_show_f_5.setText("")
            self.face.btn_show_f_6.setText("")
            self.face.btn_show_f_7.setText("")
            self.face.btn_show_f_8.setText("")
            self.face.btn_show_f_9.setText("")
            self.face.btn_show_f_num.setText("")
            self.face.btn_show_f_loss.setText("")

    def expanding_nodes_show(self, expanding_nodes):
        try:
            node1 = expanding_nodes[0]
            self.face.btn_show_e_1_1.setText(node1[0][0])
            self.face.btn_show_e_1_2.setText(node1[0][1])
            self.face.btn_show_e_1_3.setText(node1[0][2])
            self.face.btn_show_e_1_4.setText(node1[0][3])
            self.face.btn_show_e_1_5.setText(node1[0][4])
            self.face.btn_show_e_1_6.setText(node1[0][5])
            self.face.btn_show_e_1_7.setText(node1[0][6])
            self.face.btn_show_e_1_8.setText(node1[0][7])
            self.face.btn_show_e_1_9.setText(node1[0][8])
            self.face.btn_show_e_1_num.setText(str(node1[1]))
            self.face.btn_show_e_1_loss.setText(str(node1[2]))
        except:
            self.face.btn_show_e_1_1.setText("")
            self.face.btn_show_e_1_2.setText("")
            self.face.btn_show_e_1_3.setText("")
            self.face.btn_show_e_1_4.setText("")
            self.face.btn_show_e_1_5.setText("")
            self.face.btn_show_e_1_6.setText("")
            self.face.btn_show_e_1_7.setText("")
            self.face.btn_show_e_1_8.setText("")
            self.face.btn_show_e_1_9.setText("")
            self.face.btn_show_e_1_num.setText("")
            self.face.btn_show_e_1_loss.setText("")
        try:
            node2 = expanding_nodes[1]
            self.face.btn_show_e_2_1.setText(node2[0][0])
            self.face.btn_show_e_2_2.setText(node2[0][1])
            self.face.btn_show_e_2_3.setText(node2[0][2])
            self.face.btn_show_e_2_4.setText(node2[0][3])
            self.face.btn_show_e_2_5.setText(node2[0][4])
            self.face.btn_show_e_2_6.setText(node2[0][5])
            self.face.btn_show_e_2_7.setText(node2[0][6])
            self.face.btn_show_e_2_8.setText(node2[0][7])
            self.face.btn_show_e_2_9.setText(node2[0][8])
            self.face.btn_show_e_2_num.setText(str(node2[1]))
            self.face.btn_show_e_2_loss.setText(str(node2[2]))
        except:
            self.face.btn_show_e_2_1.setText("")
            self.face.btn_show_e_2_2.setText("")
            self.face.btn_show_e_2_3.setText("")
            self.face.btn_show_e_2_4.setText("")
            self.face.btn_show_e_2_5.setText("")
            self.face.btn_show_e_2_6.setText("")
            self.face.btn_show_e_2_7.setText("")
            self.face.btn_show_e_2_8.setText("")
            self.face.btn_show_e_2_9.setText("")
            self.face.btn_show_e_2_num.setText("")
            self.face.btn_show_e_2_loss.setText("")
        try:
            node3 = expanding_nodes[2]
            self.face.btn_show_e_3_1.setText(node3[0][0])
            self.face.btn_show_e_3_2.setText(node3[0][1])
            self.face.btn_show_e_3_3.setText(node3[0][2])
            self.face.btn_show_e_3_4.setText(node3[0][3])
            self.face.btn_show_e_3_5.setText(node3[0][4])
            self.face.btn_show_e_3_6.setText(node3[0][5])
            self.face.btn_show_e_3_7.setText(node3[0][6])
            self.face.btn_show_e_3_8.setText(node3[0][7])
            self.face.btn_show_e_3_9.setText(node3[0][8])
            self.face.btn_show_e_3_num.setText(str(node3[1]))
            self.face.btn_show_e_3_loss.setText(str(node3[2]))
        except:
            self.face.btn_show_e_3_1.setText("")
            self.face.btn_show_e_3_2.setText("")
            self.face.btn_show_e_3_3.setText("")
            self.face.btn_show_e_3_4.setText("")
            self.face.btn_show_e_3_5.setText("")
            self.face.btn_show_e_3_6.setText("")
            self.face.btn_show_e_3_7.setText("")
            self.face.btn_show_e_3_8.setText("")
            self.face.btn_show_e_3_9.setText("")
            self.face.btn_show_e_3_num.setText("")
            self.face.btn_show_e_3_loss.setText("")
        try:
            node4 = expanding_nodes[3]
            self.face.btn_show_e_4_1.setText(node4[0][0])
            self.face.btn_show_e_4_2.setText(node4[0][1])
            self.face.btn_show_e_4_3.setText(node4[0][2])
            self.face.btn_show_e_4_4.setText(node4[0][3])
            self.face.btn_show_e_4_5.setText(node4[0][4])
            self.face.btn_show_e_4_6.setText(node4[0][5])
            self.face.btn_show_e_4_7.setText(node4[0][6])
            self.face.btn_show_e_4_8.setText(node4[0][7])
            self.face.btn_show_e_4_9.setText(node4[0][8])
            self.face.btn_show_e_4_num.setText(str(node4[1]))
            self.face.btn_show_e_4_loss.setText(str(node4[2]))
        except:
            self.face.btn_show_e_4_1.setText("")
            self.face.btn_show_e_4_2.setText("")
            self.face.btn_show_e_4_3.setText("")
            self.face.btn_show_e_4_4.setText("")
            self.face.btn_show_e_4_5.setText("")
            self.face.btn_show_e_4_6.setText("")
            self.face.btn_show_e_4_7.setText("")
            self.face.btn_show_e_4_8.setText("")
            self.face.btn_show_e_4_9.setText("")
            self.face.btn_show_e_4_num.setText("")
            self.face.btn_show_e_4_loss.setText("")

    def brother_nodes_show(self, brother_nodes):
        try:
            node1 = brother_nodes[0]
            self.face.btn_show_b_1_1.setText(node1[0][0])
            self.face.btn_show_b_1_2.setText(node1[0][1])
            self.face.btn_show_b_1_3.setText(node1[0][2])
            self.face.btn_show_b_1_4.setText(node1[0][3])
            self.face.btn_show_b_1_5.setText(node1[0][4])
            self.face.btn_show_b_1_6.setText(node1[0][5])
            self.face.btn_show_b_1_7.setText(node1[0][6])
            self.face.btn_show_b_1_8.setText(node1[0][7])
            self.face.btn_show_b_1_9.setText(node1[0][8])
            self.face.btn_show_b_1_num.setText(str(node1[1]))
            self.face.btn_show_b_1_loss.setText(str(node1[2]))
        except:
            self.face.btn_show_b_1_1.setText("")
            self.face.btn_show_b_1_2.setText("")
            self.face.btn_show_b_1_3.setText("")
            self.face.btn_show_b_1_4.setText("")
            self.face.btn_show_b_1_5.setText("")
            self.face.btn_show_b_1_6.setText("")
            self.face.btn_show_b_1_7.setText("")
            self.face.btn_show_b_1_8.setText("")
            self.face.btn_show_b_1_9.setText("")
            self.face.btn_show_b_1_num.setText("")
            self.face.btn_show_b_1_loss.setText("")
        try:
            node2 = brother_nodes[1]
            self.face.btn_show_b_2_1.setText(node2[0][0])
            self.face.btn_show_b_2_2.setText(node2[0][1])
            self.face.btn_show_b_2_3.setText(node2[0][2])
            self.face.btn_show_b_2_4.setText(node2[0][3])
            self.face.btn_show_b_2_5.setText(node2[0][4])
            self.face.btn_show_b_2_6.setText(node2[0][5])
            self.face.btn_show_b_2_7.setText(node2[0][6])
            self.face.btn_show_b_2_8.setText(node2[0][7])
            self.face.btn_show_b_2_9.setText(node2[0][8])
            self.face.btn_show_b_2_num.setText(str(node2[1]))
            self.face.btn_show_b_2_loss.setText(str(node2[2]))
        except:
            self.face.btn_show_b_2_1.setText("")
            self.face.btn_show_b_2_2.setText("")
            self.face.btn_show_b_2_3.setText("")
            self.face.btn_show_b_2_4.setText("")
            self.face.btn_show_b_2_5.setText("")
            self.face.btn_show_b_2_6.setText("")
            self.face.btn_show_b_2_7.setText("")
            self.face.btn_show_b_2_8.setText("")
            self.face.btn_show_b_2_9.setText("")
            self.face.btn_show_b_2_num.setText("")
            self.face.btn_show_b_2_loss.setText("")
        try:
            node3 = brother_nodes[2]
            self.face.btn_show_b_3_1.setText(node3[0][0])
            self.face.btn_show_b_3_2.setText(node3[0][1])
            self.face.btn_show_b_3_3.setText(node3[0][2])
            self.face.btn_show_b_3_4.setText(node3[0][3])
            self.face.btn_show_b_3_5.setText(node3[0][4])
            self.face.btn_show_b_3_6.setText(node3[0][5])
            self.face.btn_show_b_3_7.setText(node3[0][6])
            self.face.btn_show_b_3_8.setText(node3[0][7])
            self.face.btn_show_b_3_9.setText(node3[0][8])
            self.face.btn_show_b_3_num.setText(str(node3[1]))
            self.face.btn_show_b_3_loss.setText(str(node3[2]))
        except:
            self.face.btn_show_b_3_1.setText("")
            self.face.btn_show_b_3_2.setText("")
            self.face.btn_show_b_3_3.setText("")
            self.face.btn_show_b_3_4.setText("")
            self.face.btn_show_b_3_5.setText("")
            self.face.btn_show_b_3_6.setText("")
            self.face.btn_show_b_3_7.setText("")
            self.face.btn_show_b_3_8.setText("")
            self.face.btn_show_b_3_9.setText("")
            self.face.btn_show_b_3_num.setText("")
            self.face.btn_show_b_3_loss.setText("")

    def previous_step(self):
        self.current_result -= 1
        if self.current_result == 0:
            self.face.btn_previous_step.setEnabled(False)
        if self.current_result == self.results_total - 2:
            self.face.btn_next_step.setEnabled(True)
        self.state_show()
    def next_step(self):
        self.current_result += 1
        if self.current_result == 1:
            self.face.btn_previous_step.setEnabled(True)
        if self.current_result == self.results_total - 1:
            self.face.btn_next_step.setEnabled(False)
            self.face.btn_show_efficiency.setText(str(self.efficiency))
        self.state_show()
    def first_step(self):
        self.current_result = 0
        self.face.btn_previous_step.setEnabled(False)
        self.face.btn_next_step.setEnabled(True)
        self.state_show()
    def last_step(self):
        self.current_result = self.results_total - 1
        self.face.btn_previous_step.setEnabled(True)
        self.face.btn_next_step.setEnabled(False)
        self.state_show()

    def rate_change(self):  # 改变帧速选中框内容时调用
        play_state = self.face.btn_play.text()
        if play_state == '暂停':
            self.current_rate = self.face.comboBox_frame_rate.currentText()
            self.current_rate = float(self.current_rate)
            self.play_time = False
            while(not self.play_thread_quit):
                pass
            new_play_thread = threading.Thread(target=self.play_restart)
            self.play_time = True
            self.play_thread_quit = False
            new_play_thread.start()

    def play_restart(self):
        while(self.play_time):
            if self.face.btn_next_step.isEnabled():
                self.face.btn_next_step.click()
                time.sleep(1 / self.current_rate)
            else:
                self.face.btn_play.setText('播放')
                self.play_time = False
        self.play_thread_quit = True

    def play(self): # 点击播放按钮调用
        if not self.face.comboBox_frame_rate.currentText():
            self.reply("请选择帧速")
            return
        if self.face.btn_play.text() == '播放':
            self.current_rate = self.face.comboBox_frame_rate.currentText()
            self.current_rate = float(self.current_rate)
            while (not self.play_thread_quit):
                pass
            self.face.btn_play.setText('暂停')
            new_play_thread = threading.Thread(target=self.play_restart)
            self.play_time = True
            self.play_thread_quit = False
            new_play_thread.start()
        else:
            self.face.btn_play.setText('播放')
            self.play_time = False
    def formatting(self):
        self.face.btn_show_c_1.setText('')
        self.face.btn_show_c_2.setText('')
        self.face.btn_show_c_3.setText('')
        self.face.btn_show_c_4.setText('')
        self.face.btn_show_c_5.setText('')
        self.face.btn_show_c_6.setText('')
        self.face.btn_show_c_7.setText('')
        self.face.btn_show_c_8.setText('')
        self.face.btn_show_c_9.setText('')
        self.face.btn_show_c_num.setText('')
        self.face.btn_show_c_loss.setText('')
        self.face.btn_show_f_1.setText("")
        self.face.btn_show_f_2.setText("")
        self.face.btn_show_f_3.setText("")
        self.face.btn_show_f_4.setText("")
        self.face.btn_show_f_5.setText("")
        self.face.btn_show_f_6.setText("")
        self.face.btn_show_f_7.setText("")
        self.face.btn_show_f_8.setText("")
        self.face.btn_show_f_9.setText("")
        self.face.btn_show_f_num.setText("")
        self.face.btn_show_f_loss.setText("")
        self.face.btn_show_b_1_1.setText("")
        self.face.btn_show_b_1_2.setText("")
        self.face.btn_show_b_1_3.setText("")
        self.face.btn_show_b_1_4.setText("")
        self.face.btn_show_b_1_5.setText("")
        self.face.btn_show_b_1_6.setText("")
        self.face.btn_show_b_1_7.setText("")
        self.face.btn_show_b_1_8.setText("")
        self.face.btn_show_b_1_9.setText("")
        self.face.btn_show_b_1_num.setText("")
        self.face.btn_show_b_1_loss.setText("")
        self.face.btn_show_b_2_1.setText("")
        self.face.btn_show_b_2_2.setText("")
        self.face.btn_show_b_2_3.setText("")
        self.face.btn_show_b_2_4.setText("")
        self.face.btn_show_b_2_5.setText("")
        self.face.btn_show_b_2_6.setText("")
        self.face.btn_show_b_2_7.setText("")
        self.face.btn_show_b_2_8.setText("")
        self.face.btn_show_b_2_9.setText("")
        self.face.btn_show_b_2_num.setText("")
        self.face.btn_show_b_2_loss.setText("")
        self.face.btn_show_b_3_1.setText("")
        self.face.btn_show_b_3_2.setText("")
        self.face.btn_show_b_3_3.setText("")
        self.face.btn_show_b_3_4.setText("")
        self.face.btn_show_b_3_5.setText("")
        self.face.btn_show_b_3_6.setText("")
        self.face.btn_show_b_3_7.setText("")
        self.face.btn_show_b_3_8.setText("")
        self.face.btn_show_b_3_9.setText("")
        self.face.btn_show_b_3_num.setText("")
        self.face.btn_show_b_3_loss.setText("")
        self.face.btn_show_e_1_1.setText("")
        self.face.btn_show_e_1_2.setText("")
        self.face.btn_show_e_1_3.setText("")
        self.face.btn_show_e_1_4.setText("")
        self.face.btn_show_e_1_5.setText("")
        self.face.btn_show_e_1_6.setText("")
        self.face.btn_show_e_1_7.setText("")
        self.face.btn_show_e_1_8.setText("")
        self.face.btn_show_e_1_9.setText("")
        self.face.btn_show_e_1_num.setText("")
        self.face.btn_show_e_1_loss.setText("")
        self.face.btn_show_e_2_1.setText("")
        self.face.btn_show_e_2_2.setText("")
        self.face.btn_show_e_2_3.setText("")
        self.face.btn_show_e_2_4.setText("")
        self.face.btn_show_e_2_5.setText("")
        self.face.btn_show_e_2_6.setText("")
        self.face.btn_show_e_2_7.setText("")
        self.face.btn_show_e_2_8.setText("")
        self.face.btn_show_e_2_9.setText("")
        self.face.btn_show_e_2_num.setText("")
        self.face.btn_show_e_2_loss.setText("")
        self.face.btn_show_e_3_1.setText("")
        self.face.btn_show_e_3_2.setText("")
        self.face.btn_show_e_3_3.setText("")
        self.face.btn_show_e_3_4.setText("")
        self.face.btn_show_e_3_5.setText("")
        self.face.btn_show_e_3_6.setText("")
        self.face.btn_show_e_3_7.setText("")
        self.face.btn_show_e_3_8.setText("")
        self.face.btn_show_e_3_9.setText("")
        self.face.btn_show_e_3_num.setText("")
        self.face.btn_show_e_3_loss.setText("")
        self.face.btn_show_e_4_1.setText("")
        self.face.btn_show_e_4_2.setText("")
        self.face.btn_show_e_4_3.setText("")
        self.face.btn_show_e_4_4.setText("")
        self.face.btn_show_e_4_5.setText("")
        self.face.btn_show_e_4_6.setText("")
        self.face.btn_show_e_4_7.setText("")
        self.face.btn_show_e_4_8.setText("")
        self.face.btn_show_e_4_9.setText("")
        self.face.btn_show_e_4_num.setText("")
        self.face.btn_show_e_4_loss.setText("")
        # self.face.lineEdit_initial_state.clear()
        # self.face.lineEdit_target.clear()
        self.face.lineEdit_open.clear()
        self.face.lineEdit_close.clear()
        self.face.comboBox_algorithm.setCurrentIndex(-1)
        self.face.comboBox_frame_rate.setCurrentIndex(-1)
        self.face.comboBox_dm.setCurrentIndex(-1)
        self.face.comboBox_heuristic.setCurrentIndex(-1)
        self.face.btn_show_efficiency.setText("")
        self.input_restore()
        self.view_btn_forbid()
        self.face.btn_start.setEnabled(True)
        self.face.btn_play.setText('播放')
        self.face.label_dm.setVisible(False)
        self.face.label_heuristic.setVisible(False)
        self.face.comboBox_dm.setVisible(False)
        self.face.comboBox_heuristic.setVisible(False)
        self.results = ""
        self.current_result = 0
        self.results_total = 0
        self.current_rate = 0
        self.play_time = False
        self.play_thread_quit = True

    def start(self):
        self.show()

