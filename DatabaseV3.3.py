# -*- coding:utf-8 -*-
# @Author: YuXuan Cao
# @Email: uncertainty@sjtu.edu.cn
# @Date: 2024/01/21 17:37
# @Description: This is the main program of the database management system, deisigned to handle screenshots and text data.
# @Version: 3.3
# @Update log: Added the function of tool tips in the inherit dialog window. Fixed some bugs related to the file saving issues when the data counts beyonds 10.
# @Note: This program is designed for Windows platform only.

# 描述：这是数据库管理系统的主程序，用于处理截图和文字数据。
# 版本：3.3
# 更新日志：增加继承对话框中的悬停提示。修复数据超过10个时文件保存问题。
# 注意：本程序仅适用于Windows平台。


import sys
import os
import pathlib
import winreg
from PyQt6.QtCore import Qt, QThread, QSize, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import *
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QComboBox,
    QDialog,
    QTextEdit,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout,
    QGridLayout,
    QMainWindow,
    QFileDialog,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QMessageBox,
    QSplitter,
    QToolTip

)
from subprocess import call
import shutil

def readConfig(selected_path):
    tempTuple = []
    if not os.path.exists(selected_path + '/DataConfig.cfg'):
        with open(selected_path + '/DataConfig.cfg', 'w', encoding='utf-8') as file:
            file.write('附加信息 材料信息 加工工艺 微观结构 服役条件 服役性能\n附加信息_数据组号 附加信息_文章编号 附加信息_文章题目\n材料信息_材料名称 材料信息_成分 材料信息_生产厂家\n加工工艺\n微观结构_晶粒尺寸 微观结构_织构 微观结构_初始位错密度 微观结构_第二相名称 微观结构_第二相尺寸 微观结构_第二相密度\n服役条件_温度 服役条件_应力 服役条件_注量率 服役条件_测试平台 服役条件_入射粒子种类\n服役性能_屈服强度 服役性能_抗拉强度 服役性能_断裂性能 服役性能_辐照蠕变 服役性能_辐照生长 服役性能_热蠕变 服役性能_拉伸曲线')
    with open(selected_path + '/DataConfig.cfg', 'r', encoding='utf-8') as file:
        for line in file:
            tempTuple.append(line.split())
    print(tempTuple)
    return tempTuple

class ScreenshotThread(QThread):
    def run(self):
        call(["cmd", "/c", "start", "ms-screenclip:"], creationflags=0x08000000)
        #用 subprocess.call 方法避免弹出控制台窗口

class DialogWindow(QDialog):
    #继承对话框
    def __init__(self, path, folder):
        super().__init__()
        self.folder = folder
        self.selected_path = path
        self.data = readConfig(self.selected_path)
        #self.parentData = tempTuple[0]
        #self.data1 = tempTuple[1]
        #self.data2 = tempTuple[2]
        #self.data3 = tempTuple[3]
        #self.data4 = tempTuple[4]
        #self.data5 = tempTuple[5]
        #self.data6 = tempTuple[6]
        self.setWindowTitle(f"请在文件树中选择要继承到 数据组{folder} 的项")
        self.setStyleSheet('background-color:#2b2b2b')
        self.setGeometry(300, 300, 700, 400)


        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.treeWidget = QTreeWidget(self)
        self.treeWidget.setStyleSheet('background-color:#f0f0f0')
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderHidden(True)
        self.layout.addWidget(self.treeWidget, 0, 0, 1, 2)
        self.treeWidget.setMouseTracking(True)
        self.treeWidget.itemClicked.connect(self.item_clicked_handler)
        self.treeWidget.itemEntered.connect(self.item_hovered_handler)

        n = 1
        #循环创建项和其子项，并删除没有对应数据的项
        currentDataNum = 1
        while os.path.exists(self.selected_path + "/" + str(n)):
            if n == folder:
                n = n + 1
                continue
            self.parentItemText = '数据组' +  str(n)
            self.parentItem = QTreeWidgetItem(self.treeWidget, [self.parentItemText])
            for self.childItemText in self.data[0]:
                flag = False
                self.childItem = QTreeWidgetItem(self.parentItem, [self.childItemText])
                self.childItem.setCheckState(0, Qt.CheckState.Unchecked)
                currentData = self.data[currentDataNum]
                #loc = locals()
                #exec('currentData = self.data{}'.format(currentDataNum))
                #currentData = loc['currentData']
                for self.grandchildItemText in currentData:
                    if not (os.path.isfile(self.selected_path + '/' + str(n) + '/' + str(n) + '_' + self.grandchildItemText + '.txt') or os.path.isfile(self.selected_path + '/' + str(n) + '/' + str(n) + '_' + self.grandchildItemText + '.png')):
                        continue
                    self.grandchildItem = QTreeWidgetItem(self.childItem, [str(n) + '_' + self.grandchildItemText]) #May be troublesome
                    self.grandchildItem.setCheckState(0, Qt.CheckState.Unchecked)
                    flag = True
                if not flag:
                    self.parentItem.removeChild(self.childItem)
                if currentDataNum == len(self.data[0]): #childItem 级别只有 len(self.data[0]) 个项
                    currentDataNum = 1
                    break
                currentDataNum = currentDataNum + 1
            n = n + 1

        self.treeWidget.itemChanged.connect(self.checkstate_changed)

        self.inheritImageButton = QPushButton("继承图像",self)
        self.inheritTextButton = QPushButton("继承文字",self)
        self.inheritImageButton.setStyleSheet('background-color:#f0f0f0')
        self.inheritImageButton.setFont(QFont('微软雅黑', 12))
        self.inheritTextButton.setStyleSheet('background-color:#f0f0f0')
        self.inheritTextButton.setFont(QFont('微软雅黑', 12))
        self.inheritImageButton.clicked.connect(self.inherit_image)
        self.inheritTextButton.clicked.connect(self.inherit_text)
        self.inheritImageButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.inheritTextButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.inheritImageButton, 1, 0, 1, 1)
        self.layout.addWidget(self.inheritTextButton, 1, 1, 1, 1)

        self.imageLabel = QLabel(self)
        self.textLabel = QLabel(self)
        self.imageLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.textLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.textLabel.setFont(QFont('微软雅黑', 11))
        self.layout.addWidget(self.imageLabel, 0, 2, 1, 1)
        self.layout.addWidget(self.textLabel, 1, 2, 1, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 5)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, 1)
        
    def item_hovered_handler(self, item):
        name = item.text(0)
        self.setToolTip(name)
        # 将name显示在一个浮动的小提示栏中
        

    def item_clicked_handler(self, item):
        name = item.text(0)
        file_path = self.selected_path + '/' + name[0] + '/' + name
        try:
            with open(file_path + '.txt', 'r') as file:
                saved_text = file.read()
                self.textLabel.setText(saved_text)
        except Exception as e:
            self.textLabel.clear()

        try:
            image = QPixmap(file_path + '.png')
            scaled_image = image.scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.imageLabel.setPixmap(scaled_image)
        except Exception as e:
            self.imageLabel.clear()

    def inherit_image(self):
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        number = 0
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == Qt.CheckState.Checked and item.childCount() == 0:
                name = item.text(0)
                file_path = self.selected_path + '/' + name[0] + '/' + name
                new_file_path = self.selected_path + '/' + str(self.folder) + '/' + str(self.folder) + name[1:]
                number = number + 1
                try:
                    shutil.copy(file_path + '.png', new_file_path + '.png')


                except Exception as e:
                    print(e)
                    number = number - 1
                    mesBox = QMessageBox(self) #用一步到位式的函数构造，则不好设置stylesheet
                    mesBox.setWindowTitle('图像不存在')
                    mesBox.setText(f'{item.text(0)} 项没有储存图像信息')
                    mesBox.setIcon(QMessageBox.Icon.Warning)
                    mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
                    mesBox.setStyleSheet("background-color:#f0f0f0")
                    mesBox.exec()


            iterator += 1

        if number == 0:

            mesBox = QMessageBox(self)
            mesBox.setWindowTitle('请先选择')
            mesBox.setText('请先在复选框中选择项，再点击继承按钮')
            mesBox.setIcon(QMessageBox.Icon.Information)
            mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
            mesBox.setStyleSheet("background-color:#f0f0f0")
            mesBox.exec()
            return

        mesBox = QMessageBox(self)
        mesBox.setWindowTitle('图像复制成功')
        mesBox.setText(f'{number} 个所选项已复制到 数据组{self.folder}')
        mesBox.setIcon(QMessageBox.Icon.Information)
        mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
        mesBox.setStyleSheet("background-color:#f0f0f0")
        mesBox.exec()


    def inherit_text(self):
        iterator = QTreeWidgetItemIterator(self.treeWidget)
        number = 0
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == Qt.CheckState.Checked and item.childCount() == 0:
                name = item.text(0)
                file_path = self.selected_path + '/' + name[0] + '/' + name
                new_file_path = self.selected_path + '/' + str(self.folder) + '/' + str(self.folder) + name[1:]
                number = number + 1
                try:
                    shutil.copy(file_path + '.txt', new_file_path + '.txt')

                except Exception as e:
                    number = number = 1
                    mesBox = QMessageBox(self)
                    mesBox.setWindowTitle('文本不存在')
                    mesBox.setText(f'{item.text(0)} 项没有储存文本信息')
                    mesBox.setIcon(QMessageBox.Icon.Warning)
                    mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
                    mesBox.setStyleSheet("background-color:#f0f0f0")
                    mesBox.exec()


            iterator += 1

        if number == 0:
            mesBox = QMessageBox(self)
            mesBox.setWindowTitle('请先选择')
            mesBox.setText('请先在复选框中选择项，再点击继承按钮')
            mesBox.setIcon(QMessageBox.Icon.Information)
            mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
            mesBox.setStyleSheet("background-color:#f0f0f0")
            mesBox.exec()
            return

        mesBox = QMessageBox(self)
        mesBox.setWindowTitle('文本复制成功')
        mesBox.setText(f'所选项已复制到 数据组{self.folder}')
        mesBox.setIcon(QMessageBox.Icon.Information)
        mesBox.setStandardButtons(QMessageBox.StandardButton.Yes)
        mesBox.setStyleSheet("background-color:#f0f0f0")
        mesBox.exec()


    def checkstate_changed(self, item, column): #对于只有一列的树状图，似乎column==0，但此处未作修改
        self.treeWidget.itemChanged.disconnect(self.checkstate_changed) #避免陷入死循环
        # 获取选中节点的子节点个数
        count = item.childCount()
        # 如果被选中
        if count == 0:
            parent = item.parent()
            sibcount = parent.childCount()
            flag1 = False
            flag2 = False
            for f in range(sibcount):
                if parent.child(f).checkState(0) == Qt.CheckState.Checked:
                    flag1 = True
                if parent.child(f).checkState(0) == Qt.CheckState.Unchecked:
                    flag2 = True
            if flag1 == False:
                parent.setCheckState(0, Qt.CheckState.Unchecked)
            elif flag2 == False:
                parent.setCheckState(0, Qt.CheckState.Checked)
            else:
                parent.setCheckState(0, Qt.CheckState.PartiallyChecked)
        else:
            if item.checkState(column) == Qt.CheckState.Checked:
                # 连同下面子子节点全部设置为选中状态
                for f in range(count):
                    if item.child(f).checkState(0) != Qt.CheckState.Checked:
                        item.child(f).setCheckState(0, Qt.CheckState.Checked)
            # 如果取消选中
            if item.checkState(column) == Qt.CheckState.Unchecked:
                # 连同下面子子节点全部设置为取消选中状态
                for f in range(count):
                    if item.child(f).checkState != Qt.CheckState.Unchecked:
                        item.child(f).setCheckState(0, Qt.CheckState.Unchecked)
        self.treeWidget.itemChanged.connect(self.checkstate_changed)

class Window(QMainWindow):
    resized = pyqtSignal()

    def __init__(self, Folderpath):
        super().__init__()

        # 窗口的基本参数，并设置背景颜色
        self.setMinimumSize(1080, 640)
        self.showMaximized()
        self.setWindowTitle("锆合金辐照变形参数数据库")
        self.setStyleSheet('background-color:#2b2b2b;')

        # 文献选择
        self.selected_path = fileDirectory(str(Folderpath), '已选择根目录，请选择（或新建）该根目录下的文献目录')
        if pathlib.Path(self.selected_path) == Folderpath:
            #print('error')
            subfolders = [subfolder for subfolder in pathlib.Path(self.selected_path).iterdir() if subfolder.is_dir()]
            first_subfolder = subfolders[0] if subfolders else None
            if first_subfolder:
                self.selected_path = str(first_subfolder)
                os.chdir(self.selected_path)
                #print('Found default dir')
            else:
                self.selected_path = self.selected_path + '\文献1'
                os.mkdir(self.selected_path, 755)
                os.chdir(self.selected_path)
                #print('Created default dir')
        else:
            os.chdir(self.selected_path)

        print(os.getcwd())

        self.data = readConfig(self.selected_path)
        self.data.pop(0)

        # 窗口布局和顶栏
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.statusLabel = QLabel(self)
        self.statusLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setText("欢迎！祝你度过愉快的一天")
        self.statusLabel.setFont(QFont('微软雅黑', 11))
        #self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 2, 3, 1, 1)

        self.usageLabel = QLabel(self)
        self.usageLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.usageLabel.setWordWrap(True)
        self.usageLabel.setText("1. 点击截屏按钮截取图像后，点击相应数据的条目保存\n2. 编辑相应条目的文本框，文本将会自动保存")
        self.usageLabel.setFont(QFont('微软雅黑', 11))
        #self.usageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.usageLabel.setObjectName("usageLabel")
        self.gridLayout.addWidget(self.usageLabel, 0, 3, 2, 1)

        self.dirLabel = QLabel(self)
        self.dirLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.dirLabel.setWordWrap(True)
        self.dirLabel.setText(f"当前的文献目录是 {self.selected_path}")
        self.dirLabel.setFont(QFont('微软雅黑', 11))
        #self.dirLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dirLabel.setObjectName("dirLabel")
        self.gridLayout.addWidget(self.dirLabel, 2, 5, 1, 1)

        self.imageLabel = QLabel(self)
        self.imageLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.gridLayout.addWidget(self.imageLabel, 0, 2, 3, 1)

        #自动调整预览大小
        self.timer = QTimer(self)
        self.previousSize = self.imageLabel.size()
        self.timer.timeout.connect(self.checkSizeChange)
        self.timer.start(200)  # 每200毫秒检查一次大小变化

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.print_Image)
        self.folder = 1

        self.box = QComboBox(self)
        self.box.setObjectName("box")
        self.box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.box.setStyleSheet('background-color:#f0f0f0')
        self.box.setFont(QFont('微软雅黑', 13))
        self.box.addItems(['数据组1', "新建数据组"])
        os.makedirs(self.selected_path + '/1', exist_ok=True)
        n = 2
        while os.path.exists(self.selected_path + "/" + str(n)):
            self.box.insertItem(n - 1, "数据组" + str(n))
            n = n + 1
        self.gridLayout.addWidget(self.box, 0, 1, 1, 1)
        self.box.setCurrentIndex(0)
        self.box.activated.connect(self.on_combobox_activated)

        #self.box2 = QComboBox(self)
        #self.box2.setObjectName("box")
        #self.box2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #self.box2.setStyleSheet('background-color:#f0f0f0')
        #self.box2.setFont(QFont('微软雅黑', 13))
        #index = 0
        #for i in sorted(Folderpath.iterdir(), key= lambda x : int(x.stem[2:])):
        #    self.box2.addItem('i.stem')
        #    if i == pathlib.Path(self.selected_path):
        #        self.box.setCurrentIndex(index)
        #    index += 1
        #self.box2.insertItem(index, '新建文献')
        #self.gridLayout.addWidget(self.box2, 0, 5, 1, 1)
        #self.box.activated.connect(self.on_combobox2_activated)
#
        spacerItem0 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed,
                                  QSizePolicy.Policy.Minimum)
        #spacerItem = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred,
        #                                   QSizePolicy.Policy.Minimum)
        spacerItem2 = QSpacerItem(30, 20, QSizePolicy.Policy.Fixed,
                                 QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem0, 0, 0, 3, 1)
        #self.gridLayout.addItem(spacerItem, 0, 5, 3, 1)
        self.gridLayout.addItem(spacerItem2, 0, 6, 3, 1) #添加一些间距，与下方ScrollArea对齐。注意此处使用的是addItem而不是addWidget

        self.button = QPushButton("截屏",self)
        #sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())
        #self.button.setSizePolicy(sizePolicy)
        self.button.setStyleSheet('background-color:#f0f0f0')
        self.button.setFont(QFont('微软雅黑', 15))
        self.button.setObjectName("button")
        self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button.clicked.connect(self.capture_screenshot)
        self.gridLayout.addWidget(self.button, 2, 1, 1, 1)

        self.guidanceLabel = QLabel(self)
        self.guidanceLabel.setStyleSheet('background-color:#3c3f41; color: white')
        self.guidanceLabel.setWordWrap(True)
        self.guidanceLabel.setText("Tips:\n• 鼠标悬停在数据组框，滚动滚轮可以快速改变数据组。\n• 也可使用 Win+Shift+S 快捷键截屏\n• 可以同时运行多个程序，记录不同文献的数据点\n• 点击‘重选文献’来更换当前的文献目录") #Guidance！
        self.guidanceLabel.setFont(QFont('微软雅黑', 11))
        #self.guidanceLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guidanceLabel.setObjectName("guidanceLabel")
        self.gridLayout.addWidget(self.guidanceLabel, 0, 4, 3, 1)

        self.inheritButton = QPushButton("继承",self)
        self.inheritButton.setObjectName("inheritButton")
        self.inheritButton.setStyleSheet('background-color:#f0f0f0')
        self.inheritButton.setFont(QFont('微软雅黑', 15))
        self.inheritButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.inheritButton.clicked.connect(self.inherit_Dialog)
        self.gridLayout.addWidget(self.inheritButton, 1, 1, 1, 1)


        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.gridLayout.setColumnStretch(3, 1)
        self.gridLayout.setColumnStretch(4, 1)
        self.gridLayout.setColumnStretch(5, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 820, 441))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        #若不能滚动，修改这个
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        #self.gridLayout_2 = QGridLayout()
        #self.gridLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        #self.gridLayout_2.setObjectName("gridLayout_2")
        #self.pushButton = QPushButton(self)
        #self.pushButton.setObjectName("pushButton")
        #self.gridLayout_3.addWidget(self.pushButton, 1, 0, 1, 1) #只是一个用来验证布局的按钮组件
        #self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)
        self.setCentralWidget(self.centralwidget)

        #self.data1 = ('附加信息_数据组号', '附加信息_文章编号', '附加信息_文章题目')
        #self.data2 = ('材料信息_材料名称', '材料信息_成分', '材料信息_生产厂家')
        #self.data3 = ('加工工艺',)
        #self.data4 = ('微观结构_晶粒尺寸', '微观结构_织构', '微观结构_初始位错密度', '微观结构_第二相名称', '微观结构_第二相尺寸', '微观结构_第二相密度')
        #self.data5 = ('服役条件_温度', '服役条件_应力', '服役条件_注量率', '服役条件_测试平台', '服役条件_入射粒子种类')
        #self.data6 = ('服役性能_屈服强度', '服役性能_抗拉强度', '服役性能_断裂性能', '服役性能_辐照蠕变', '服役性能_辐照生长', '服役性能_热蠕变', '服役性能_拉伸曲线')
        #self.data = [self.data1, self.data2, self.data3, self.data4, self.data5, self.data6]
        #self.dataList = self.data1 + self.data2 + self.data3 + self.data4 + self.data5 + self.data6

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.print_Image)
        self.folder = 1
        #self.properties = self.data[0]

        self.create_MainFabric()
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)

        self.openDirButton = QPushButton("打开文献目录",self)
        self.openDirButton.setStyleSheet('background-color:#f0f0f0')
        self.openDirButton.setFont(QFont('微软雅黑', 15))
        self.openDirButton.setObjectName("openDirButton")
        self.openDirButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.openDirButton.clicked.connect(self.open_Dir)
        self.gridLayout.addWidget(self.openDirButton, 1, 5, 1, 1)

        self.restartButton = QPushButton("重选文献",self)
        self.restartButton.setStyleSheet('background-color:#f0f0f0')
        self.restartButton.setFont(QFont('微软雅黑', 15))
        self.restartButton.setObjectName("openDirButton")
        self.restartButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.restartButton.clicked.connect(self.restart)
        self.gridLayout.addWidget(self.restartButton, 0, 5, 1, 1)

    def restart(self):
        app.exit(100)

    def open_Dir(self):
        os.startfile(self.selected_path)

    def create_MainFabric(self):
        currentColumn = 0 #额虽然听起来很蠢但是还是备注一下：Column是列，Row是行
        currentRow = 0
        dataNum = 0
        dataNum2 = 0
        self.textList = []
        self.labelList = []
        self.buttonList = []

        for data in self.data:
            self.buttonTempList = []
            self.labelTempList = []
            self.textTempList = []

            for datum in data:
                self.splitter = QSplitter(self)
                self.splitter.setOrientation(Qt.Orientation.Horizontal)
                self.splitter.setMinimumSize(1, 1)
                self.splitter.setStyleSheet('background-color:#747a80')
                self.gridLayout_3.addWidget(self.splitter, currentRow, 0, 1, 5)

                self.pushButton = QPushButton(datum, self)
                self.pushButton.setObjectName(f"pushButton{dataNum}-{dataNum2}")
                self.pushButton.setStyleSheet('background-color:#f0f0f0')
                self.pushButton.setFont(QFont('微软雅黑', 13))
                self.buttonTempList.append(self.pushButton)
                self.pushButton.clicked.connect(self.save_screenshot)
                self.gridLayout_3.addWidget(self.pushButton, currentRow + 1, currentColumn, 1, 1)

                self.label = QLabel(self)
                self.label.setObjectName(f"label{dataNum}-{dataNum2}")
                self.label.setText("")
                self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.label.setStyleSheet('background-color:#3c3f41')
                self.imageLabel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
                #self.label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                #self.label.setScaledContents(True)
                self.labelTempList.append(self.label)
                self.gridLayout_3.addWidget(self.label, currentRow + 2, currentColumn, 1, 1)

                self.textEdit = QTextEdit(self)
                self.textEdit.setObjectName(f"textEdit{dataNum}-{dataNum2}")
                self.textEdit.setPlaceholderText("在此处输入附加文本，将自动保存")
                self.textEdit.setStyleSheet('background-color:#d4d6d9')
                self.textEdit.setFont(QFont('微软雅黑', 11))
                self.textEdit.textChanged.connect(self.save_Text)
                self.textTempList.append(self.textEdit)
                self.gridLayout_3.addWidget(self.textEdit, currentRow + 3, currentColumn, 1, 1)

                dataNum2 += 1
                if currentColumn == 4:
                    currentColumn = 0
                    currentRow += 4 #分隔的splitter占一行
                else:
                    currentColumn += 1

            currentColumn = 0
            currentRow += 4
            dataNum2 = 0
            self.textList.append(self.textTempList)
            self.labelList.append(self.labelTempList)
            self.buttonList.append(self.buttonTempList)
            dataNum += 1

    def checkSizeChange(self):
        if self.imageLabel.size() != self.previousSize:
            self.resized.emit()
            self.show_Data()
            #self.print_Image()
            self.previousSize = self.imageLabel.size()
            print('Resized')
            #self.timer.timeout.disconnect(self.checkSizeChange)
            #self.timer.stop()

    def on_combobox_activated(self, index):
        selected_item = self.box.itemText(index)
        if selected_item == "新建数据组":
            # 新建数据组的处理逻辑
            new_item = "数据组" + str(self.box.currentIndex() + 1)  # 在上一个选项的值的基础上加1
            self.box.insertItem(index, new_item)  # 插入新建的选项
            self.box.setCurrentIndex(index)  # 将选中项设为新建的选项
            os.makedirs(self.selected_path + f'/{index+1}', exist_ok=True)

        self.folder = index + 1
        self.show_Data()

    def capture_screenshot(self):
        self.thread = ScreenshotThread()
        self.thread.start()
        self.statusLabel.clear()

    def print_Image(self):
        # 将剪贴板中的图像显示在预览框imageLabel中
        image = self.clipboard.image()

        if not image.isNull():
            scaled_image = image.scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.imageLabel.setPixmap(QPixmap.fromImage(scaled_image))
        else:
            pass

    def save_Text(self):
        
        print((self.sender()).objectName())

        currentNum = int((((self.sender()).objectName()).split('t')[-1]).split('-')[0])
        currentNum2 = int((((self.sender()).objectName()).split('t')[-1]).split('-')[1])

        file_path = self.selected_path + f'/{self.folder}/{self.folder}_{self.data[currentNum][currentNum2]}.txt'
        text = (self.sender()).toPlainText()
        if not text and os.path.isfile(file_path):

            os.remove(file_path)

        if text:
            try:
                with open(file_path, 'w') as file:
                    file.write(text)
                    #print("!!!")
            except Exception as e:
                print(f'保存文件时出错：{str(e)}')

    def save_screenshot(self):
        #print(self.labelList[3])

        currentNum = int((((self.sender()).objectName()).split('n')[-1]).split('-')[0])
        currentNum2 = int((((self.sender()).objectName()).split('n')[-1]).split('-')[1])

        #currentNum = int(((self.sender()).objectName())[10:11]) #通过字符串处理，将被激活的按钮的 ObjectName 尾部的序号提取出来作为 Index
        #currentNum2 = int(((self.sender()).objectName())[12:13]) #注意 Num2 是二维元组的第二个数，Num 同理
        
        #print((self.sender()).objectName())
        
        # 获取剪贴板的图像数据
        image = self.clipboard.image()
        if not image.isNull():
            #os.makedirs(self.selected_path + f'/{self.folder}', exist_ok=True)
            os.chdir(self.selected_path + f'/{self.folder}')

            image.save(f"{self.folder}_{self.data[currentNum][currentNum2]}.png")
            self.statusLabel.setText(f"已保存图像为\n{self.folder}_{self.data[currentNum][currentNum2]}.png")

            os.chdir(self.selected_path)
        self.show_Image(currentNum, currentNum2)

    def show_Image(self, dataNum, dataNum2):
        (self.labelList[dataNum][dataNum2]).clear()
        image = QImage(self.selected_path + f'/{self.folder}/{self.folder}_{self.data[dataNum][dataNum2]}.png')
        if not image.isNull():
            scaled_image = image.scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            (self.labelList[dataNum][dataNum2]).setPixmap(QPixmap.fromImage(scaled_image))
        else:
            pass

    def show_Data(self):
        dataNum = 0
        dataNum2 = 0
        print(self.imageLabel.geometry())
        print((self.labelList[dataNum][dataNum2]).geometry())
        while dataNum < len(self.data):
            while dataNum2 < len(self.data[dataNum]):
                self.show_Image(dataNum, dataNum2)
                #if os.path.exists(self.selected_path + f'/{self.folder}/{self.folder}_{self.data[dataNum][dataNum2]}.png'):
#
                #    image = QImage(self.selected_path + f'/{self.folder}/{self.folder}_{self.data[dataNum][dataNum2]}.png')
                #    scaled_image = image.scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio,
                #                                Qt.TransformationMode.SmoothTransformation)
                #    (self.labelList[dataNum][dataNum2]).setPixmap(QPixmap.fromImage(scaled_image))
                #else:
                #    #print(f'{dataNum}-{dataNum2} cleared')
                #    #self.statusLabel.setText(f"请先截屏，再点击保存")
                #    (self.labelList[dataNum][dataNum2]).clear()
                #print(f'dataNum={dataNum2}')

                (self.textList[dataNum][dataNum2]).textChanged.disconnect(self.save_Text)
                (self.textList[dataNum][dataNum2]).clear()
                try:
                    with open(self.selected_path + f'/{self.folder}/{self.folder}_{self.data[dataNum][dataNum2]}.txt', 'r') as file:
                        saved_text = file.read()
                        (self.textList[dataNum][dataNum2]).setPlainText(saved_text)
                except Exception as e:
                    pass
                    #(self.textList[dataNum][dataNum2]).clear()
                (self.textList[dataNum][dataNum2]).textChanged.connect(self.save_Text)

                dataNum2 += 1
            #print(f'dataNum2={dataNum}')
            dataNum += 1
            dataNum2 = 0

    def inherit_Dialog(self):
        dialog = DialogWindow(self.selected_path, self.folder)
        dialog.exec()
        self.show_Data()
        self.statusLabel.clear()


#通过注册表获得当前的桌面路径
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
desktopDir = winreg.QueryValueEx(key, "Desktop")[0]

def fileDirectory(Dir, Title):

    #显示文件选择窗口
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.FileMode.Directory)  # 设置对话框模式为选择目录
    dialog.setDirectory(Dir)
    dialog.setWindowTitle(Title)
    result = dialog.exec()
    selected_path = dialog.selectedFiles()
    if result == 0:
        return 0
    else:
        return selected_path[0]

app = QApplication(sys.argv)
selected_path = fileDirectory(desktopDir, '请选择（或新建）作为数据库根目录的文件夹')
Folderpath = pathlib.Path(selected_path)
newFolderpath = Folderpath / '锆合金数据库'

if str(Folderpath)[-6:] == '锆合金数据库':
    os.chdir(Folderpath)
else:
    if not newFolderpath.exists():
        os.mkdir(newFolderpath,755)
    os.chdir(newFolderpath)
    Folderpath = newFolderpath

while True:
    window = Window(Folderpath)
    window.show()
    code = app.exec()
    print(code)
    if code != 100:
        break