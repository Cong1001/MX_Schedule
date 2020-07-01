#!/usr/bin/env python3.6

import sys
from settings import GetSettings
from AWS_MX_Schedule import AWS_Schedule
from Check import check_file
from CatchAccount import get_account_list

if __name__ == '__main__':
    settings = GetSettings()
    fail_list_file = settings.fail_tmp_file
    account_list_file = check_file(settings.REGION)
    account_list = get_account_list(account_list_file, settings.REGION)
    for account in account_list:
        account_id = account_list[account]['ID']
        account_name = account_list[account]['Name']
        account_region = account_list[account]['Region']
        try:
            AWS_Schedule(account_id, account_name, account_region)
        except:
            print('ERROR: schedule ' + account_name + ' error!')
            e = sys.exc_info()[1]
            print("%s" %e)
            with open(fail_list_file, 'a') as fail_list:
                fail_list.write('Customer ID: ' + account_name + '\n' + 'Error info: ' + str(e) + '\n')
            fail_list.close()
