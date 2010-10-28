#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys, os
from subprocess import *

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QApplication, QDialog, QMessageBox, QLayout
from Ui_csrwindow import Ui_CSRWindow

class CSRAssistant(QDialog, Ui_CSRWindow):
	def __init__(self):
		QDialog.__init__(self)
		self.setupUi(self)

	@pyqtSignature("")
	def on_btnGenerate_clicked(self):
		if self.txtDomain.text() == "":
			QMessageBox.warning(self, "Missing field", "You must specify a domain name")
			self.txtDomain.setFocus()
			return
		if self.txtCountry.text() == "":
			QMessageBox.warning(self, "Missing field", "You must specify a country")
			self.txtCountry.setFocus()
			return
		if self.txtStateProvince.text() == "":
			QMessageBox.warning(self, "Missing field", "You must specify a state or province")
			self.txtStateProvince.setFocus()
			return
		if self.txtLocality.text() == "":
			QMessageBox.warning(self, "Missing field", "You must specify a locality")
			self.txtLocality.setFocus()
			return
		if self.txtOrganization.text() == "":
			QMessageBox.warning(self, "Missing field", "You must specify an organization name")
			self.txtOrganization.setFocus()
			return

		domain = self.txtDomain.text()
		keyfile = os.path.expanduser("~/%s.key" % domain)
		csrfile = os.path.expanduser("~/%s.csr" % domain)
		self.lblHostKey.setText("Private host key: %s" % keyfile)
		self.lblCSR.setText("Certificate request: %s" % csrfile)

		csrdata = "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s/" % (
			self.txtCountry.text(),
			self.txtStateProvince.text(),
			self.txtLocality.text(),
			self.txtOrganization.text(),
			self.txtOrganizationUnit.text(),
			self.txtDomain.text()
		)

		p = Popen(["openssl", "req", "-new", "-subj", csrdata, "-nodes", "-keyout", keyfile, "-out", csrfile], shell=False, stderr=STDOUT, stdout=PIPE)
		QMessageBox.information(self, "Generation result", p.communicate()[0])

		if self.chkSign.checkState() == Qt.Checked:
			crtfile = os.path.expanduser("~/%s.crt" % domain)
			p = Popen(["openssl", "x509", "-req", "-days", "30", "-in", csrfile, "-signkey", keyfile, "-out", crtfile], shell=False, stderr=STDOUT, stdout=PIPE)
			QMessageBox.information(self, "Signing result", p.communicate()[0])

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = CSRAssistant()
	window.show()
	sys.exit(app.exec_())
