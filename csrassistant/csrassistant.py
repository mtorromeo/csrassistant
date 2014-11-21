#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
from subprocess import *
from tempfile import NamedTemporaryFile

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QLayout
from Ui_csrwindow import Ui_CSRWindow


class CSRAssistant(QDialog, Ui_CSRWindow):
    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)

    def run(self, command):
        p = Popen(command, shell=False, stderr=STDOUT, stdout=PIPE)
        return p.communicate()[0].decode("utf-8")

    @pyqtSlot()
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

        csrdata = "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s/emailAddress=%s/" % (
            self.txtCountry.text(),
            self.txtStateProvince.text(),
            self.txtLocality.text(),
            self.txtOrganization.text(),
            self.txtOrganizationUnit.text(),
            self.txtDomain.text(),
            self.txtEmail.text()
        )

        if self.cmbAlgorithm.currentText() == "ECDSA":
            ecparam = NamedTemporaryFile(delete=False)
            ecparam.close()

            out = self.run(["openssl", "ecparam", "-name", "secp256k1", "-out", ecparam.name])
            if out:
                QMessageBox.information(self, "Ecparam generation result", out)
            algo = "ec:{}".format(ecparam.name)
        else:
            algo = "rsa:2048"

        out = self.run(["openssl", "req", "-new", "-sha256", "-subj", csrdata, "-nodes", "-newkey", algo, "-keyout", keyfile, "-out", csrfile])
        if out:
            QMessageBox.information(self, "Generation result", out)

        if self.cmbAlgorithm.currentText() == "ECDSA":
            os.unlink(ecparam.name)

        if self.chkSign.checkState() == Qt.Checked:
            crtfile = os.path.expanduser("~/%s.crt" % domain)
            out = self.run(["openssl", "x509", "-req", "-days", str(self.spinDays.value()), "-in", csrfile, "-signkey", keyfile, "-out", crtfile])
            if out:
                QMessageBox.information(self, "Signing result", out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSRAssistant()
    window.show()
    sys.exit(app.exec_())
