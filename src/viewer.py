#!/usr/bin/env python
# -*- coding: utf-8 -*-

import coords
import game
import json
import os
import sys
import wx
import wx.lib.newevent

# Main window title
TITLE = 'Chtuhlu Fhtagn'

# Control IDs
ID_BOARD_SELECT_BTN = 101
ID_COMMANDS_SELECT_BTN = 102
ID_LOAD_BTN = 103
ID_STEP_BTN = 104
ID_RUN_BTN = 105
ID_RUN_EVENT = 150

RunSimEvent, EVT_RUN_SIM = wx.lib.newevent.NewCommandEvent()

class Viewer(wx.Frame):
    def __init__(self, board_file, commands_file):
        wx.Frame.__init__(self, None, -1, TITLE, size = (1000, 800), style = wx.DEFAULT_FRAME_STYLE)
        # Frame initializations.
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetMinSize((500, 300))
        # Child control initializations.
        self._board_input = wx.TextCtrl(self, -1, board_file)
        self._board_label = wx.StaticText(self, -1, 'Board file:')
        self._board_select_btn = wx.Button(self, ID_BOARD_SELECT_BTN, 'Select')
        self._commands_input = wx.TextCtrl(self, -1, commands_file)
        self._commands_label = wx.StaticText(self, -1, 'Commands file:')
        self._commands_select_btn = wx.Button(self, ID_COMMANDS_SELECT_BTN, 'Select')
        self._load_btn = wx.Button(self, ID_LOAD_BTN, 'Load')
        self._step_btn = wx.Button(self, ID_STEP_BTN, 'Step')
        self._step_input = wx.SpinCtrl(self, -1, '1', min=1, max=3000000, initial=1)
        self._run_btn = wx.Button(self, ID_RUN_BTN, 'Run')
        self._canvas = Canvas(self)
        self._canvas.EnableScrolling(True, True)
        # Sizer layout.
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._board_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._commands_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._canvas_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._canvas_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._command_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_sizer.Add(self._board_sizer, 0, flag = wx.EXPAND)
        self._main_sizer.Add(self._commands_sizer, 0, flag = wx.EXPAND)
        self._main_sizer.Add(self._canvas_area_sizer, 1, flag = wx.EXPAND)
        self._board_sizer.Add(self._board_label, 1, flag = wx.ALIGN_LEFT)
        self._board_sizer.Add(self._board_input, 7, flag = wx.EXPAND)
        self._board_sizer.Add(self._board_select_btn, 0, flag = wx.ALIGN_RIGHT)
        self._commands_sizer.Add(self._commands_label, 1, flag = wx.ALIGN_LEFT)
        self._commands_sizer.Add(self._commands_input, 7, flag = wx.EXPAND)
        self._commands_sizer.Add(self._commands_select_btn, 0, flag = wx.ALIGN_RIGHT)
        self._canvas_area_sizer.Add(self._command_sizer, 0, flag = wx.EXPAND)
        self._canvas_area_sizer.Add(self._canvas_sizer, 1, flag = wx.EXPAND)
        self._canvas_sizer.Add(self._canvas, 1, flag = wx.EXPAND)
        self._command_sizer.Add(self._load_btn, 0, flag = wx.EXPAND)
        self._command_sizer.Add(self._step_btn, 0, flag = wx.EXPAND)
        self._command_sizer.Add(self._step_input, 0, flag = wx.EXPAND)
        self._command_sizer.Add(self._run_btn, 0, flag = wx.EXPAND)
        self.SetSizer(self._main_sizer)
        # Status bar definitions.
        bar = self.CreateStatusBar(8)
        bar.SetStatusWidths([-2, -2, -2, -2, -2, -2, -2, -3])
        # Event initializations.
        self.Bind(wx.EVT_BUTTON, self.OnBoardSelectBtn, id = ID_BOARD_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnCommandsSelectBtn, id = ID_COMMANDS_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnLoadBtn, id = ID_LOAD_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnStepBtn, id = ID_STEP_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnRunBtn, id = ID_RUN_BTN)
        self.Bind(EVT_RUN_SIM, self.OnRunEvent, id = ID_RUN_EVENT)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKey)
        # Game object.
        self.game = None
        self._game_running = False
        self._game_step = 0
        self._commands = []
        # load file if there
        if board_file:
            self.Load(board_file, commands_file)
        # Show window.
        self.Move((10, 10))
        self.Show()

    # Event handlers.
    def OnBoardSelectBtn(self, event):
        #print 'OnBoardSelectBtn'
        dlg = wx.FileDialog(self,
                            'Open board file',
                            wildcard = 'JSON (*.json)|*.json',
                            style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self._board_input.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnCommandsSelectBtn(self, event):
        dlg = wx.FileDialog(self,
                            'Open commands file',
                            wildcard = 'JSON (*.json)|*.json',
                            style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self._commands_input.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnLoadBtn(self, event):
        #print 'OnLoadBtn'
        board_path = self._board_input.GetValue()
        commands_path = self._commands_input.GetValue()
        self.Load(board_path, commands_path)

    def Load(self, board_path, commands_path):
        if board_path:
            self.game = game.Problem.load(board_path).make_game(0)
        else:
            units = [game.Unit((1,1), [(0,0), (1,0), (0,1)])]
            board = game.Board(10, 10, [(1, 1)])
            self.game = game.Game(board, units, 17)
        try:
            with open(commands_path) as cf:
                solutions = json.loads(cf.read())
                # For now, just use the first one
                solution = solutions[0]["solution"]
                self._commands = [x for x in solution]
        except IOError:
            print "Commands file not found"
            pass

        self._game_step = 0
        w, h = self.game.size
        self._canvas.SetBoardSize(w, h)
        self.UpdateStatusBar()

    def OnStepBtn(self, event):
        #print 'OnStepBtn'
        self.Run(int(self._step_input.GetValue()))

    def OnRunBtn(self, event):
        #print 'OnRunBtn'
        if self._game_running:
            self._game_running = False
            self._run_btn.SetLabel('Run')
        else:
            self._game_running = True
            self._run_btn.SetLabel('Stop')
            self.AddPendingEvent(RunSimEvent(id=ID_RUN_EVENT))

    def OnRunEvent(self, event):
        #print 'OnRunEvent'
        self.Run(int(self._step_input.GetValue()))

    def OnClose(self, event):
        #print 'OnClose'
        self.Destroy()

    def OnKey(self, event):
        if isinstance(event.EventObject, wx.TextCtrl):
            event.Skip()
            return
        kc = event.GetKeyCode()
        if kc == ord('E'):
             self.MakeMove('b')
        elif kc == ord('W'):
            self.MakeMove('p')
        elif kc == ord('S'):
            self.MakeMove('a')
        elif kc == ord('D'):
            self.MakeMove('l')
        else:
            event.Skip()

    def AcceptsFocus(self):
        return True

    def DirectionFromCommand(self, c):
        dirs = {"p": "W",
                "'": "W",
                "!": "W",
                ".": "W",
                "0": "W",
                "3": "W",
                "b": "E",
                "c": "E",
                "e": "E",
                "f": "E",
                "y": "E",
                "2": "E",
                "a": "SW",
                "g": "SW",
                "h": "SW",
                "i": "SW",
                "j": "SW",
                "4": "SW",
                "l": "SE",
                "m": "SE",
                "n": "SE",
                "o": "SE",
                " ": "SE",
                "5": "SE",
                "d": "CW",
                "q": "CW",
                "r": "CW",
                "v": "CW",
                "z": "CW",
                "1": "CW",
                "k": "CCW",
                "s": "CCW",
                "t": "CCW",
                "u": "CCW",
                "w": "CCW",
                "x": "CCW"
        }
        coord_dirs = {
            "W": coords.DIRECTION_W,
            "E": coords.DIRECTION_E,
            "SE": coords.DIRECTION_SE,
            "SW": coords.DIRECTION_SW
        }
        return coord_dirs[dirs[c]]

    def Run(self, steps):
        while steps > 0 and self._game_step < len(self._commands):
            self.game.move_unit(self.DirectionFromCommand(self._commands[self._game_step]))
            self._game_step += 1
            steps -= 1
        if self._game_running:
            if self._game_step < len(self._commands):
                self.AddPendingEvent(RunSimEvent(id=ID_RUN_EVENT))
            else:
                self._run_btn.SetLabel('Run')
                self._game_running = False

        self._canvas.Refresh()
        self.UpdateStatusBar()

    def MakeMove(self, move):
        commands = self._commands
        self._commands = commands[0:self._game_step] + [move] + commands[self._game_step:]
        self.Run(1)

    def UpdateStatusBar(self):
        bar = self.GetStatusBar()
        score = 0
        if self.game:
            score = self.game.score
        bar.SetStatusText("Score: %d"%(score,), 0)

class Canvas(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, -1)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # Ensure scrollbars are used
        self.SetBoardSize(10, 10)

    def OnSize(self, event):
        #print 'Canvas.OnSize'
        pass

    def OnPaint(self, event):
        #print 'Canvas.OnPaint'
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.LIGHT_GREY_BRUSH)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc);
        gc.SetFont(wx.FontFromPixelSize((12,12), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.WHITE)
        parent = self.GetParent()
        if parent.game is not None:
            for y in range(self._yw):
                for x in range(self._xw):
                    obj = parent.game.cell(x, y)
                    cols = {game.CELL_EMPTY: wx.Colour(40, 40, 40, 255),
                            game.CELL_FILLED: wx.Colour(20, 20, 255, 255),
                            game.CELL_UNIT: wx.Colour(255, 20, 20, 255)}
                    col = cols[obj]
                    p = self.CalcScrolledPosition((x*32 + 16 * (y % 2), y*27))
                    gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255), 1))
                    gc.SetBrush(wx.Brush(col))
                    px, py = p
                    points = [(px, py + 9), (px + 16, py), (px + 32, py + 9), (px + 32, py + 27), (px + 16, py + 36), (px, py + 27)]
                    gc.DrawLines(points)

    def SetBoardSize(self, xw, yw):
        self._xw = xw
        self._yw = yw
        self._xp = 32 * (xw + 1)
        self._yp = 27 * (yw + 1)
        self.UpdateBoardSize()

    def UpdateBoardSize(self):
        # Size in world coordinates.
        self.SetClientSize((self._xp, self._yp))
        self.SetScrollbars(1, 1, self._xp, self._yp)
        self.SetScrollRate(32, 32)
        self.Refresh()

if __name__ == '__main__':
    board_file = ''
    commands_file = ''
    if len(sys.argv) > 1:
        board_file = sys.argv[1]
    if len(sys.argv) > 2:
        commands_file = sys.argv[2]
    app = wx.App(False)
    viewer = Viewer(board_file, commands_file)
    app.MainLoop()
