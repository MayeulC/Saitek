#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout,
                             QProgressBar, QSlider, QTabWidget,
                             QVBoxLayout, QSpinBox, QGroupBox,
                             QPushButton, QCheckBox)

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QObject

import usb1
import copy

# Device list definition. If you want to add a device, this is likely where you will
# want to start. Check your mouse product and vendor ID with `lsusb` (the output is
# vid:pid), and add it to the list, using the ones that are present as an example.
# You can then submit a pull request on GitHub, open an issue or report it in #4.

# Vendor list. Changes are unlikely to happen here. Recent devices are probably
# MadCatz ones.
vendorList = {0x06a3: 'Saitek',
              0x0738: 'Mad Catz'}

# Product list, sorted by PID
products = [
# Saitek
            {'vid': 0x06a3, 'pid': 0x0cc3, 'name': 'Cyborg R.A.T.5'},  # @noobish's mouse (#4)
            {'vid': 0x06a3, 'pid': 0x0ccb, 'name': 'old Cyborg R.A.T.7'},  # present in the Linux kernel: drivers/hid/hid-ids.h@866
            {'vid': 0x06a3, 'pid': 0x0ccc, 'name': 'Cyborg R.A.T.3'},  # from Arch wiki
            {'vid': 0x06a3, 'pid': 0x0cd7, 'name': 'Cyborg R.A.T.9', 'battery': True},  # present in the Linux kernel: drivers/hid/hid-ids.h@867
            {'vid': 0x06a3, 'pid': 0x0cd9, 'name': 'Cyborg R.A.T.9', 'battery': True},  # @MaikuMori's mouse (pull #1)
            {'vid': 0x06a3, 'pid': 0x0cfa, 'name': 'Cyborg R.A.T.9', 'battery': True, 'dpi': 5600},  # @MayeulC 's mouse
# Mad Catz
            {'vid': 0x0738, 'pid': 0x1705, 'name': 'R.A.T 5'},  # @np's mouse (fork)
            {'vid': 0x0738, 'pid': 0x1709, 'name': 'R.A.T 9', 'battery': True},  # @improti's mouse (fork)
            {'vid': 0x0738, 'pid': 0x1718, 'name': 'R.A.T PRO X'}]  # @Angelus's mouse (#8 - not tested)


# Code begins here


class DeviceComms:
    def __init__(self):
        self.handle = 0
        self.context = 0
        self.hasHandle = 0
        self.hasContext = 0
        self.ctrl_request_type = 0
        self.ctrl_request = 0
        self.ctrl_value = 0
        self.ctrl_index = 0
        self.ctrl_length = 0
        self.currentDevice = {}
        self.initiate()

    def initiate(self):
        if not self.hasContext:
            self.getContext()
        if not self.hasHandle:
            self.getHandle()

    def getContext(self):
        try:
            self.context = usb1.USBContext()
            self.hasContext = 1
        except:
            self.hasContext = 0

    def findDevices(self):
        try:
            deviceList = self.context.getDeviceList()
        except:
            print("Could not enumerate USB devices")
            exit(-1)

        devicesFound = []
        for device in deviceList:
            if device.getVendorID() in vendorList:
                for p in products:
                    if p['vid'] == device.getVendorID() and p['pid'] == device.getProductID():
                        print("Found one device:", p)  # DEBUG!! user-facing debug message. To delete later.
                        devicesFound.append(p)
        return devicesFound

    def getHandle(self):
        self.handle = None
        self.hasHandle = 0
        devicesFound = self.findDevices()
        # TODO: nicely ask the user which device he wants to open, and allow change at runtime
        # if there is more than one device. For now, we just open the first one.
        idx = 0
        if not devicesFound:
            print("No compatible device found. Please retry or file a bug")
            exit(-1)
            # TODO: allow to retry, force open a device, and show a list of candidates
        try:
            self.handle = self.context.openByVendorIDAndProductID(
                devicesFound[idx]['vid'], devicesFound[idx]['pid'])
        except:
            print("Error during handle acquisition, do you have the right permissions?")
            exit(-1)

        if self.handle:
            self.hasHandle = 1
            self.currentDevice = devicesFound[idx]
        else:
            print("This shouldn't have happened. Did not get a device handle after trying to get one, please file a bug")
            exit(-1)

    def getCurrentMouseName(self):
        if 'name' in self.currentDevice:
            return self.currentDevice['name']
        else:
            return 'no mouse detected'

    def getDpi(self, dpi):
        if not self.hasContext or not self.hasHandle:
            return
        self.ctrl_request_type = 0xc0
        self.ctrl_request = 144
        self.ctrl_value = 0
        self.ctrl_length = 2

        for mode in range(0, 4):
            for axis in range(0, 2):
                self.ctrl_index = 0x0073
                self.ctrl_index += 0x1000 * (mode + 1)
                self.ctrl_index += 0x0100 * (axis + 1)
                measure = self.controlRead()
                dpi.setDpiData(25 * measure[1] + 100, mode, axis)

    def getBatteryLevel(self):
        if not ('battery' in self.currentDevice) or not self.currentDevice['battery']:
            return 0
        self.ctrl_request_type = 0xc0
        self.ctrl_request = 144
        self.ctrl_value = 0
        self.ctrl_index = 186
        self.ctrl_length = 1
        battery = self.controlRead()
        return battery[0]

    def getDpiMode(self):
        self.ctrl_request_type = 0xc0
        self.ctrl_request = 144
        self.ctrl_value = 0
        self.ctrl_index = 116
        self.ctrl_length = 1
        mode = self.controlRead()
        return mode[0] / 16

    def sendDpi(self, dpi):
        self.ctrl_request_type = 0x40
        self.ctrl_request = 145
        self.ctrl_index = 115
        self.ctrl_length = b''
        for mode in range(0, 4):
            for axis in range(0, 2):
                self.ctrl_value = 0x1000 * (mode + 1)
                self.ctrl_value += 0x0100 * (axis + 1)
                normalized_dpi = int((dpi.getDpiData(mode, axis) - 100) / 25)
                self.ctrl_value += 0x0001 * normalized_dpi
                self.controlWrite()
        # Followed by a validation packet.
        self.ctrl_index = 112
        self.ctrl_value = 0x51
        self.controlWrite()
        if self.hasHandle:
            dpi.dataHasBeenSent()

    def sendMode(self, Mode):
        # With 0<= Mode <=3.
        self.ctrl_request_type = 0x40
        self.ctrl_request = 145
        self.ctrl_index = 116
        self.ctrl_length = b''
        self.ctrl_value = 0x1000 * (Mode + 1)
        self.controlWrite()

    def resetDpi(self):
        self.ctrl_request_type = 0x40
        self.ctrl_request = 145
        self.ctrl_index = 115
        self.ctrl_length = b''
        self.ctrl_value = 0x0000
        # Reset packet.
        self.controlWrite()
        # Followed by a validation packet.
        self.ctrl_index = 112
        self.ctrl_value = 0x51
        self.controlWrite()

    def controlRead(self):
        try:
            measure = self.handle.controlRead(self.ctrl_request_type,
                                              self.ctrl_request,
                                              self.ctrl_value,
                                              self.ctrl_index,
                                              self.ctrl_length)
            return measure
        except:
            self.hasHandle = 0
            return self.ctrl_length * [None]

    def controlWrite(self):
        try:
            self.handle.controlWrite(self.ctrl_request_type,
                                     self.ctrl_request,
                                     self.ctrl_value, self.ctrl_index,
                                     self.ctrl_length)
        except:
            self.hasHandle = 0


class Data(QWidget):
    def __init__(self, pbar, tabs, dpi, com):
        super().__init__()
        self.dpi = dpi
        self.com = com
        self.pbar = pbar
        self.tabs = tabs
        self.battery = 0
        self.dpiMode = 0
        self.lastDpiMode = 0
        self.pool()

    def pool(self):
        self.dpiMode = self.com.getDpiMode()
        self.battery = self.com.getBatteryLevel()
        self.displayResults()

    def sendDpi(self):
        self.com.sendDpi(self.dpi)

    def displayResults(self):
        self.pbar.setValue(self.battery)
        if self.dpiMode != self.lastDpiMode:
            # `dpiMode` starts at 1.
            self.tabs.setCurrentIndex(self.dpiMode - 1)
            self.lastDpiMode = self.dpiMode

    def timerEvent(self, e):
        self.pool()


class DPI(QObject):
    def __init__(self):
        super().__init__()
        self.dpi = [[None, None],
                    [None, None],
                    [None, None],
                    [None, None]]
        self.populateDefaultDpiValues()
        self.oldDpi = copy.deepcopy(self.dpi)

    def populateDefaultDpiValues(self):
        for i in range(0, 2):
            self.dpi[0][i] = 800
            self.dpi[1][i] = 1600
            self.dpi[2][i] = 3200
            self.dpi[3][i] = 5600
            self.dataChanged.emit()

    def getDpiData(self, mode, axis):
        return self.dpi[mode][axis]

    def setDpiData(self, dpi, mode, axis):
        self.dpi[mode][axis] = dpi
        self.dataChanged.emit()

    def hasChanged(self):
        if self.oldDpi == self.dpi:
            return 0
        else:
            return 1

    def dataHasBeenSent(self):
        self.oldDpi = copy.deepcopy(self.dpi)

    dataChanged = pyqtSignal()


class DPIAdjustmentTab(QWidget):
    def __init__(self, identifier, dpi, com):
        super().__init__()
        # The sliders are `ratio` times bigger than the right hand
        # corner buttons.
        ratio = 2
        layout = QGridLayout()
        vlayout = []
        self.identifier = identifier
        self.dpi = dpi
        self.com = com
        self.setLayout(layout)
        self.sliders = []
        self.spinboxes = []
        self.containers = []
        titles = ['X', 'Y']
        for i in range(0, 2):
            vlayout.append(QVBoxLayout())
            self.sliders.append(QSlider(Qt.Vertical))
            self.containers.append(QGroupBox(titles[i]))
            self.containers[i].setLayout(vlayout[i])
            self.spinboxes.append(QSpinBox())
            self.spinboxes[i].setRange(100, 5600)
            self.spinboxes[i].setSingleStep(25)
            self.sliders[i].setSingleStep(25)
            self.sliders[i].setMinimum(100)
            self.sliders[i].setTickInterval(800)
            self.sliders[i].setPageStep(800)
            self.sliders[i].setMaximum(5600)
            vlayout[i].addWidget(self.spinboxes[i])
            vlayout[i].addWidget(self.sliders[i])
            layout.addWidget(self.containers[i], 0, ratio * i, 4, 2)
            self.sliders[i].valueChanged.connect(self.spinboxes[i].setValue)
            self.spinboxes[i].valueChanged.connect(self.sliders[i].setValue)
        self.sliders[0].valueChanged.connect(self.changexDpi)
        self.sliders[1].valueChanged.connect(self.changeyDpi)
        self.moveSlidersTogether(1)
        self.checkbox = QCheckBox("Move sliders together")
        self.checkbox.setChecked(1)
        self.resetButton = QPushButton("Reset to defaults")
        self.sendButton = QPushButton("Apply")
        self.sendButton.setDisabled(1)
        layout.addWidget(self.checkbox, 1, 2 * ratio + 1)
        layout.addWidget(self.resetButton, 2, 2 * ratio + 1)
        layout.addWidget(self.sendButton, 3, 2 * ratio + 1)
        self.checkbox.stateChanged.connect(self.moveSlidersTogether)
        self.resetButton.clicked.connect(self.dpi.populateDefaultDpiValues)
        self.dpi.dataChanged.connect(self.updateViewFromData)
        self.updateViewFromData()

    def moveSlidersTogether(self, val):
        if val == 0:
            self.sliders[0].valueChanged.disconnect(self.sliders[1].setValue)
            self.sliders[1].valueChanged.disconnect(self.sliders[0].setValue)
        else:
            self.sliders[0].valueChanged.connect(self.sliders[1].setValue)
            self.sliders[1].valueChanged.connect(self.sliders[0].setValue)

    def updateViewFromData(self):
        for i in range(0, 2):
            self.sliders[i].setValue(self.dpi.getDpiData(self.identifier, i))
        if self.dpi.hasChanged() == 0:
            self.sendButton.setDisabled(1)
        else:
            self.sendButton.setDisabled(0)

    def changexDpi(self, dpi):
        self.dpi.setDpiData(dpi, self.identifier, 0)

    def changeyDpi(self, dpi):
        self.dpi.setDpiData(dpi, self.identifier, 1)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.com = DeviceComms()
        self.setWindowTitle('ratctl - ' + self.com.getCurrentMouseName())
        self.pbar = QProgressBar()
        self.pbar.setFormat("Battery : %p%")
        self.grid = QGridLayout()

        self.setLayout(self.grid)
        self.grid.addWidget(self.pbar)
        self.grid.addWidget(self.tabs)

        self.dpi = DPI()
        self.t = []  # table of tabs
        for i in range(0, 4):
            self.t.append(DPIAdjustmentTab(i, self.dpi, self.com))
            self.tabs.addTab(self.t[i], "Mode " + str(i + 1))

        self.data = Data(self.pbar, self.tabs, self.dpi, self.com)
        for i in range(0, 4):
            self.t[i].sendButton.clicked.connect(self.data.sendDpi)
            self.t[i].resetButton.clicked.connect(self.com.resetDpi)
        self.timer = QBasicTimer()  # Timer to periodically update information
        self.timer.start(100, self.data)
        self.tabs.currentChanged.connect(self.com.sendMode)  # Changes the mode when changing tabs
        self.com.getDpi(self.dpi)
        self.dpi.dataHasBeenSent()


def main():
    app = QApplication(sys.argv)

    w = MainWindow()

    w.resize(800, 600)
    w.move(300, 300)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
