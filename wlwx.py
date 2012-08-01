#!/usr/bin/env python2

#########################################################################
# programme	: wordlist-gui.py                                       #
# description	: wxpython interface for wordlist                       #
# last edit	: 31-Jul-2012                                           #
#	by	: Johannes Englisch                                     #
#########################################################################

import os
import sys
import wx
from wordlist import WordList

class ViewText(wx.Frame):
	'''simple text viewer window
	
	attributes:
		text		the text to be displayed
		textctrl	the control displaying the text
	'''

	def __init__(self, text, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)
		self.text = text
		self.init_ui()
		self.Show()
		self.update_text()

	def init_ui(self):
		'''initialise user interface'''
		self.SetTitle('View text')
		self.SetSize((300, 300))
		# text view
		self.textctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		self.textctrl.SetEditable(False)

	def update_text(self):
		'''update text field'''
		self.textctrl.SetValue(self.text)


class TableDND(wx.FileDropTarget):
	'''make wordlist table a target for file drag'n'drop

	attributes:
		self.window	drop target
	'''

	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window

	def OnDropFiles(self, x, y, filenames):
		'''load wordlist on file drop'''
		if len(filenames) > 1:
			return
		self.window.GetParent().load_wordlist(filenames[0])
		self.window.GetParent().update_table()


class MainWindow(wx.Frame):
	'''main window for wordlist programme
	
	attributes:
		dirname		directory of the text file
		filname		file name of the text file
		statusbar	the statusbar widget
		table		the table showing the wordlist
		textview	the ViewText window
		wordlist	the wordlist
	'''

	def __init__(self, filename, stoplists=None, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)
		self.dirname = ''
		self.filename = ''
		self.statusbar = None
		self.wordlist = None
		if filename:
			self.load_wordlist(filename)
		self.textview = None
		self.init_ui()
		self.Show()
		self.update_table()

	def init_ui(self):
		'''initialise user interface'''
		self.SetSize((350, 400))
		self.SetTitle('Wordlist')
		# menubar
		self.menubar = wx.MenuBar()
		menufile = wx.Menu()
		fileopen = menufile.Append(wx.ID_OPEN, '&Open\tCtrl-O',
				'Open a text file and create a wordlist from it')
		filesave = menufile.Append(wx.ID_SAVE, '&Save\tCtrl-S',
				'Save the wordlist to a text file')
		filequit = menufile.Append(wx.ID_EXIT, '&Quit\tCtrl-Q',
				'Quit the Wordlist programme')
		self.menubar.Append(menufile, '&File')
		menuview = wx.Menu()
		viewbyword = menuview.AppendRadioItem(-1, 'Sort by beginning of &word\tCtrl-1',
				'Sort the wordlist by the beginning of the words')
		viewbyend = menuview.AppendRadioItem(-1 , 'Sort by &end of word\tCtrl-2',
				'Sort the wordlist by the end of the words')
		viewbyfreq = menuview.AppendRadioItem(-1, 'Sort by &frequency\tCtrl-3',
				'Sort the wordlist by the occurences of the words')
		self.menubar.Append(menuview, '&View')
		menutools = wx.Menu()
		toolsview = menutools.Append(-1, '&View text\tCtrl-T',
				'View the text the wordlist was created from')
		self.menubar.Append(menutools, '&Tools') 
		self.SetMenuBar(self.menubar)
		# menu events
		self.Bind(wx.EVT_MENU, self.on_open, fileopen)
		self.Bind(wx.EVT_MENU, self.on_save, filesave)
		self.Bind(wx.EVT_MENU, self.on_quit, filequit)
		self.Bind(wx.EVT_MENU, self.on_viewtext, toolsview)
		# menu accelerators
		accelerators = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('O'), wx.ID_OPEN),
			(wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE),
			(wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT),
			(wx.ACCEL_CTRL, ord('1'), viewbyword.GetId()),
			(wx.ACCEL_CTRL, ord('2'), viewbyend.GetId()),
			(wx.ACCEL_CTRL, ord('3'), viewbyfreq.GetId()),
			(wx.ACCEL_CTRL, ord('T'), toolsview.GetId()),
			])
		self.SetAcceleratorTable(accelerators)
		# toolbar
		self.toolbar = self.CreateToolBar()
		tb_open = self.toolbar.AddLabelTool(wx.ID_OPEN, label='Open',
				bitmap=wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN),
				shortHelp='Open text file',
				longHelp='Open a text file and create a wordlist from it')
		tb_save = self.toolbar.AddLabelTool(wx.ID_SAVE, label='Save',
				bitmap=wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE),
				shortHelp='Save wordlist',
				longHelp='Save the wordlist to a text file')
		tb_viewtext = self.toolbar.AddLabelTool(wx.ID_ANY, label='View text',
				bitmap=wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE),
				shortHelp='View text',
				longHelp='View the text the wordlist was created from')
		self.Bind(wx.EVT_TOOL, self.on_open, tb_open)
		self.Bind(wx.EVT_TOOL, self.on_save, tb_save)
		self.Bind(wx.EVT_TOOL, self.on_viewtext, tb_viewtext)
		self.toolbar.Realize()
		# statusbar
		self.statusbar = self.CreateStatusBar()
		# table
		self.table = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		self.table.InsertColumn(0, 'word')
		self.table.InsertColumn(1, 'frequency')
		# table drag'n'drop
		droptarget = TableDND(self.table)
		self.table.SetDropTarget(droptarget)

	def load_wordlist(self, filename):
		'''load wordlist from file'''
		if self.statusbar:
			self.statusbar.SetStatusText('Reading data from file...')
		with open(filename, 'r') as f:
			text = unicode(f.read(), 'utf-8')
		self.wordlist = WordList(text)
		if self.statusbar:
			self.statusbar.SetStatusText('Data read.')
		self.dirname = os.path.dirname(filename)
		self.filename = os.path.basename(filename)

	def on_open(self, event):
		'''open a text file and generate wordlist'''
		dialog = wx.FileDialog(self, message='', defaultDir=self.dirname,
				defaultFile=self.filename, wildcard='*', style=wx.OPEN)
		answer = dialog.ShowModal()
		if answer == wx.ID_OK:
			self.load_wordlist(dialog.GetPath())
			self.update_table()
		dialog.Destroy()

	def on_save(self, event):
		'''save wordlist to text file'''
		dialog = wx.FileDialog(self, message='', defaultDir=self.dirname,
				defaultFile=self.filename, wildcard='*', style=wx.SAVE)
		answer = dialog.ShowModal()
		if answer == wx.ID_OK:
			raise NotImplementedError('Saving files not implemented, yet')
		dialog.Destroy()

	def on_quit(self, event):
		'''quit programme'''
		self.Close()

	def on_viewtext(self, event):
		'''view the text'''
		if self.textview:
			self.textview.text = self.wordlist.text
			self.textview.update_text()
			self.textview.SetFocus()
		else:
			self.textview = ViewText(self.wordlist.text, self)

	def update_table(self):
		'''refill the table with the content of the wordlist'''
		self.statusbar.SetStatusText('Updating wordlist...')
		self.table.DeleteAllItems()
		if self.wordlist:
			for i in sorted(self.wordlist.items()):
				self.table.Append(i)
		self.statusbar.SetStatusText('Wordlist updated.')


def main(args):
	filename = ''
	if len(args) > 1:
		filename = args[1]
	app = wx.App()
	MainWindow(filename, None)
	app.MainLoop()


if __name__ == "__main__":
	main(sys.argv)


