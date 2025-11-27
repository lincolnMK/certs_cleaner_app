import unittest
from unittest.mock import Mock, patch
from tkinter import messagebox
from gui.main_gui import CertCleanerGUI

class TestCertCleanerGUI(unittest.TestCase):

    def setUp(self):
        self.root = Mock()
        self.app = CertCleanerGUI(self.root)
        self.callback = Mock()

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror') 
    def test_run_stage_clean_certs(self, mock_error, mock_info):
        # Setup
        self.app.notebook.select = Mock(return_value='tab1')
        self.app.notebook.tab = Mock(return_value='Clean Certs')
        self.app.cert_input.get = Mock(return_value='/input')
        self.app.cert_output.get = Mock(return_value='/output')
        self.app.tlma_code.get = Mock(return_value='TLMA1')
        self.app.ta_code_optional.get = Mock(return_value='TA1')
        self.app.dry_run_var.get = Mock(return_value=False)

        # Execute
        self.app._run_stage(self.callback)

        # Assert
        self.callback.assert_called_once_with('/input', '/output', 'TLMA1', 'TA1', False, self.app._write_log)
        mock_info.assert_called_once_with('Success', 'Clean Certs stage completed.')
        mock_error.assert_not_called()

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    def test_run_stage_clean_title_plans(self, mock_error, mock_info):
        # Setup
        self.app.notebook.select = Mock(return_value='tab2')
        self.app.notebook.tab = Mock(return_value='Clean Title Plans')
        self.app.title_plan_input.get = Mock(return_value='/input')
        self.app.title_plan_output.get = Mock(return_value='/output')
        self.app.dry_run_var.get = Mock(return_value=False)

        # Execute
        self.app._run_stage(self.callback)

        # Assert  
        self.callback.assert_called_once_with('/input', '/output', None, None, False, self.app._write_log)
        mock_info.assert_called_once_with('Success', 'Clean Title Plans stage completed.')
        mock_error.assert_not_called()

    @patch('tkinter.messagebox.showerror')
    def test_run_stage_error(self, mock_error):
        # Setup
        self.app.notebook.select = Mock(return_value='invalid')
        self.app.notebook.tab = Mock(return_value='Invalid Tab')

        # Execute
        self.app._run_stage(self.callback)

        # Assert
        self.callback.assert_not_called()
        mock_error.assert_called_once_with('Error', 'Something went wrong:\nUnknown tab selected.')

if __name__ == '__main__':
    unittest.main()