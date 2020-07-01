from os import environ

class GetSettings(object):
    def __init__(self):
        self.SingleCustomer = environ.get('SingleCustomer', None)
        self.CustomerID = environ.get('CustomerID', None)
        self.Cloud = environ.get('Cloud', None)
        self.REGION = environ.get('Region', None)
        self.Year = environ.get('Year', None)
        self.Month = environ.get('Month', None)
        self.Day = environ.get('Day', None)
        self.Hour = environ.get('Hour', None)
        self.Minute = environ.get('Minute', None)

        self.dev_window_name = 'DEV_Patch_MW'
        self.prd_window_name = 'PRD_Patch_MW'
        self.task_name = 'Install_Patch'
        self.linux_cacheclean_task = 'Linux_Cache_Clean'
        self.linux_cacheclean_cmd = 'yum clean all'
        self.fail_tmp_file = './tmp/fail_list'
        self.no_tag_tmp_file = './tmp/no_tag_list'
        self.aws_customer_list_dir = './Customer_List/AWS'
        self.Exception_List_File = './Customer_List/AWS/Exception_List.json'
        self.Baseline_Settings_File = './PatchBaselineSettings/BaselineSettings.json'
