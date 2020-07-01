#!/usr/bin/env python3.6

import os, sys, re
from settings import GetSettings

def out():
    settings = GetSettings()
    fail_file_path = settings.fail_tmp_file
    no_tag_file_path = settings.no_tag_tmp_file

    if os.path.exists(fail_file_path) or os.path.exists(no_tag_file_path):
        if os.path.exists(no_tag_file_path):
            with open(no_tag_file_path, 'r') as no_tag_file:
                no_tag_text = no_tag_file.read()
                no_tag_num = len(re.findall(r'Customer ID:', no_tag_text))
                no_tag_output = 'No Patch Group tag customer number: ' + str(no_tag_num) + '\n' + no_tag_text
                print(no_tag_output)
        if os.path.exists(fail_file_path):
            with open(fail_file_path, 'r') as fail_file:
                fail_text = fail_file.read()
                fail_num = len(re.findall(r'Customer ID:', fail_text))
                fail_output = 'Fail customer number: ' + str(fail_num) + '\n' + fail_text
                print(fail_output)
        
        sys.exit(1)
    else:
        print("Congratulation! No error occurred during this schedule!")
        
if __name__ == '__main__':
    out()
