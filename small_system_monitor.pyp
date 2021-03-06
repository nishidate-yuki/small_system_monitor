"""
Small System Monitor in C4D

Copyright (c) 2020 Nishiki

Released under the MIT license
https://opensource.org/licenses/mit-license.php
"""

import os
import sys
import c4d
abs_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_dir)
import psutil


PLUGIN_ID = 1054769

CPU_COLOR = c4d.Vector(0.3, 0.64, 1)
MEMORY_COLOR = c4d.Vector(1, 0.9, 0.3)
C4D_MEMORY_COLOR = c4d.Vector(1, 0.64, 0.3)
BACKGROUND_COLOR = c4d.Vector(50/255.0)

BAR_HEIGHT = 3
INTERVAL_TIME_MS = 1000


class CPUArea(c4d.gui.GeUserArea):
    def Init(self):
        self.Update()
        return

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)
        self.DrawSetPen(BACKGROUND_COLOR)
        self.DrawRectangle(x1, y1, x2, y2)

        # cpu usage
        cpu = psutil.cpu_percent(0.1)
        x = (x2 - x1) * (cpu / 100.0)
        self.DrawSetPen(CPU_COLOR)
        self.DrawRectangle(x1, y1, x, y2)

        return

    def Update(self):
        self.Redraw()
        return


class MemoryArea(c4d.gui.GeUserArea):
    def Init(self):
        self.Update()
        return

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)
        self.DrawSetPen(BACKGROUND_COLOR)
        self.DrawRectangle(x1, y1, x2, y2)

        # memory usage
        memory = psutil.virtual_memory() 
        x = (x2 - x1) * (float(memory.used) / memory.total)
        self.DrawSetPen(MEMORY_COLOR)
        self.DrawRectangle(x1, y1, x, y2)

        # memory usage by c4d
        c4d_memory = c4d.storage.GeGetMemoryStat()
        x = (x2 - x1) * (float(c4d_memory[c4d.C4D_MEMORY_STAT_MEMORY_INUSE]) / memory.total)
        self.DrawSetPen(C4D_MEMORY_COLOR)
        self.DrawRectangle(x1, y1, x, y2)

        return

    def Update(self):
        self.Redraw()
        return


class SystemMonitor(c4d.gui.GeDialog):
    def __init__(self):
        self.cpu_info = CPUArea()
        self.mem_info = MemoryArea()

    def CreateLayout(self):
        self.SetTitle("Small System Monitor")

        # cpu area
        if self.GroupBegin(id=1100, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=c4d.BORDER_GROUP_IN):
            self.GroupBorderSpace(5, 0, 5, 0)
            self.cpu_text = self.AddStaticText(id=1101, initw=80, inith=0, name="CPU", borderstyle=0, flags=c4d.BFH_LEFT)
            cpu_area = self.AddUserArea(id=1102, flags=c4d.BFH_SCALEFIT, inith=BAR_HEIGHT)
            self.AttachUserArea(self.cpu_info, cpu_area)
        self.GroupEnd()

        # memory area
        if self.GroupBegin(id=1200, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=c4d.BORDER_GROUP_IN):
            self.GroupBorderSpace(5, 0, 5, 5)
            self.mem_text = self.AddStaticText(id=1201, initw=80, inith=0, name="Memory", borderstyle=0, flags=c4d.BFH_LEFT)
            memory_area = self.AddUserArea(id=1202, flags=c4d.BFH_SCALEFIT, inith=BAR_HEIGHT)
            self.AttachUserArea(self.mem_info, memory_area)
        self.GroupEnd()

        return True

    def InitValues(self):
        self.SetTimer(INTERVAL_TIME_MS)
        return True

    def Timer(self, msg):
        self.cpu_info.Update()
        self.mem_info.Update()


class SystemMonitorCommandData(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = SystemMonitor()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaulth=0, defaultw=300)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = SystemMonitor()
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    directory, _ = os.path.split(__file__)
    img_path = os.path.join(directory, "res", "small_system_monitor.tif")
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")
    if bmp.InitWith(img_path)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID, str="SmallSystemMonitor",
                                      help="Show the current cpu and memory usage.",
                                      info=0, dat=SystemMonitorCommandData(), icon=bmp)
