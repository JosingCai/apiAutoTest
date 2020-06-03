#!/usr/bin/env python
# -*- coding: utf-8 -*-

from local.function.comModVar import *
from local.function.base import *
from local.apicase import runTargetAPI

test_report_def = {"moudule1": "moudule1_TestCase_Base.xls", "moudule2": "moudule2_TestCase_Base.xls"}

class TestCase(object):
    def __init__(self, project):
        self.project = project
        Keys = test_report_def.keys()
        count = 0
        for Key in Keys:
            count = count + 1
            if Key in project.lower():
                test_case_file_name = "local/CASE/%s" %test_report_def[Key]
                break
            if count == len(Keys):
                test_case_file_name = "local/CASE/%s" %"Common_TestCase_Base.xls"
        self.handle = Excel(test_case_file_name)

    def get_sheet_names(self):
        sheet_names = self.handle.read_sheet_names()
        index = list(range(len(sheet_names)))
        index_list = []
        for i in index:
            index_dict = {}
            index_dict["index"] = i
            index_dict["name"] = sheet_names[i]
            index_list.append(index_dict)
        return index_list

    def get_sheet_content(self, sheet_name):
        contents = self.handle.read_sheet_content(sheet_name)
        return contents

    def delete_case(self, sheet_name, **request_info):
        case_num = list(request_info.keys())[0]
        status, output = self.handle.delete_excel_row(sheet_name, case_num)
        print(status, output)
        return status, output

    def modify_case(self, sheet_name, **request_info):
        Keys = list(request_info.keys())
        case_info = []
        for Key in Keys:
            case_info.append(request_info[Key].strip())
        status, output = self.handle.modify_excel_row(sheet_name, case_info[1:])
        print(status, output)
        return status, output

    def add_case(self, sheet_name, **request_info):
        case_type_def = {"base_fun": "基本功能测试", "scene": "场景测试", "abnormal": "异常测试", "longtime": "长时间测试", "pressure": "压力测试", "ui_interactive": "UI交互测试", "security": "安全测试"}
        case_level_def = {"level0": "Level0", "level1": "Level1", "level2": "Level2", "level3": "Level3", "level4": "Level4", "level5": "Level5"}
        case_auto_test_def = {"yes": "是", "no": "否"}
        case_test_reulst_def = {"untest": "未测试", "pass": "PASS", "fail": "FAIL", "un_merge": "未合入", "deprecated": "废弃"}

        request_info["case_type"] = case_type_def[request_info["case_type"]]
        request_info["priority"] = case_level_def[request_info["priority"]]
        request_info["auto_test"] = case_auto_test_def[request_info["auto_test"]]
        request_info["test_result"] = case_test_reulst_def[request_info["test_result"]]

        info_list = [request_info["case_num"].strip(), request_info["case_name"].strip(), request_info["case_type"], request_info["priority"],request_info["pre_condition"], request_info["test_range"], request_info["test_steps"],request_info["expected_result"],request_info["auto_test"],request_info["related_api"], request_info["fun_dev"], request_info["test_design"], request_info["test_operator"],request_info["test_date"], request_info["test_result"], request_info["remark"]]

        status, output = self.handle.add_row_data(sheet_name, info_list)
        print(status, output)
        return status, output

    def split_case(self, sheet_name):
        status, output = self.handle.split_table(sheet_name)
        print(status, output)
        return status, output

    def run_case(self, sheet_name, **request_info):
        case_num = list(request_info.keys())[0]
        status, output = self.handle.get_case_info(sheet_name, case_num)
        if status:
            isAuto = output[8]
            autoAPI = output[9]
            if isAuto == '是' and len(autoAPI) != 0:
                status, output = runTargetAPI(self.project, autoAPI)
                self.handle.modify_case_status(sheet_name, case_num, status)
                return status, output
            else:
                return False, "%s Not Support Auto Test or Not Related API info, Please Check it " %(case_num)
        return status, output
