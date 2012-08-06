#!/usr/bin/env python2

#########################################################################
# programme	: finddlg.py                                            #
# description	: simple search dialogue                                #
# last edit	: 06-Aug-2012                                           #
#	by	: Johannes Englisch                                     #
#########################################################################

import wx

class FindDlg(wx.Dialog):
	'''dialogue for entering search terms
	
	attributes:
		searchterm	the term to be searched for
		textctrl	the control displaying the stoplist
	'''

	def __init__(self, parent, *args, **kwargs):
		wx.Dialog.__init__(self, parent, *args, **kwargs)
		self.searchterm = ''
		self.init_ui()
		self.textctrl.SetFocus()
	
	def init_ui(self):
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(wx.StaticText(self, id = wx.ID_ANY, label = 'Enter search term:'))
		# text control
		self.textctrl = wx.TextCtrl(self)
		vbox.Add(self.textctrl, flag = wx.EXPAND)
		# buttons
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		butok = wx.Button(self, wx.ID_OK, '&Ok')
		butcancel = wx.Button(self, wx.ID_CANCEL, '&Close')
		hbox.Add(butok)
		hbox.Add(butcancel)
		vbox.Add(hbox, flag = wx.ALIGN_RIGHT)
		self.SetSizer(vbox)
		self.Fit()
		# events
		butok.Bind(wx.EVT_BUTTON, self.on_ok)

	def on_ok(self, event):
		'''OK button applies search term'''
		self.searchterm = self.textctrl.GetValue().lower()
		self.EndModal(wx.ID_OK)


