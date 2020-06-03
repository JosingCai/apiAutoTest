#!/usr/bin/env python
# -*- coding: utf-8 -*-

from local.function.comModVar import *
#from comModVar import *

def createDir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    return True
    
def humanReadable(filePath):
    try:
        os.popen('iconv -f UTF8 -t GB18030 %s > %s.tmp'%(filePath,filePath))
        os.popen('mv %s.tmp %s'%(filePath,filePath))
        return True
    except Exception as e:
        print("exception: ", e)
        return False

def logRecord(string, file_path, Type=0):
        info = {0: "Info", 1: "Error"}
        curTime=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        String = "[ %s ] %s: %s\n"%(curTime, info[Type], string)
        if DEBUG is True:
            print(String)
        with open(file_path, 'a+') as f:
            f.write(String)

def transUnicode2str(**info):
    infoDict = {}
    Keys = info.keys()
    for Key in Keys:
        tmpKey = Key.encode("utf-8")
        infoDict[tmpKey] = info[Key]
    return infoDict


class rawConfigParser(ConfigParser.ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=defaults, allow_no_value=True)

    def optionxform(self, optionstr):
        return optionstr


class localConfigParser(ConfigParser.ConfigParser):
    """docstring for localConfigParser"""
    def __init__(self, fileName):
        self.fileName = fileName
        self.config = rawConfigParser()
        self.config.read(fileName)
    
    def getOption(self, section, option):
        ret = self.config.has_option(section, option)
        if ret is not True:
            #print "%s file with no %s section or %s option"%(self.fileName, section, option)
            return False
        value = self.config.get(section, option)
        return value

    def getSection(self, section):
        ret = self.config.has_section(section)
        if ret is not True:
            #print "%s file with no %s section"%(self.fileName, section)
            return False
        values = self.config.items(section)
        return dict(values)

    def getAllSection(self):
        ret = self.config.sections()
        return ret

    def getAllOption(self, section):
        ret = self.config.options(section)
        return ret

    def getAllItem(self, section):
        ret = self.config.items(section)
        return dict(ret)

    def hasSection(self, section):
        return self.config.has_section(section)

    def writeSection(self, section, option, value):
        if not self.hasSection(section):
            self.config.add_section(section)
        self.config.set(section,option,str(value))
        with open(self.fileName,"w+") as f:
            self.config.write(f)
        return True

    def removeSection(self, section):
        status = self.config.remove_section(section)
        with open(self.fileName, "w+") as fp:
            self.config.write(fp)
        if status:
            return True, "Remove %s Section Success ~ "%(section)
        else:
            return False, "Remove %s Section Failed ~ "%(section)

    def removeOption(self, section, option):
        status = self.config.remove_option(section, option)
        with open(self.fileName, "w+") as fp:
            self.config.write(fp)
        if status:
            return True, "Remove %s : %s Success ~ "%(section, option)
        else:
            return True, "Remove %s : %s Failed ~ "%(section, option)


class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print("exception: ", e)
            return {}

def get_db_config(module):
    hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))
    SQLString = hf.getOption(module, "DBCONFIG")
    if not SQLString:
        return False, "Not Found DBCONFIG Parameter, Please check it ~"
    str_list = SQLString.split(":")
    db_info = {}
    db_info["db_user"] = str_list[0]
    db_info["db_pwd"] = str_list[1]
    db_info["db_ip"] = str_list[2]
    db_info["db_port"] = str_list[3]
    db_info["db_name"] = str_list[4]
    return True, db_info


class RawAPI(object):
    """docstring for RawAPI"""
    def __init__(self,  module, apiString):
        self.apiDict = {}
        # print "apiString: ", apiString
        apiList = apiString.replace("\"", "").split("|")
        try:
            self.apiDict["APIFunction"] = apiList[0]
            self.apiDict["http_method"] = apiList[2]
            self.apiDict["path"] = apiList[3]
            if len(apiList[5]) != 0:
                self.apiDict["pathVariable"] = eval(apiList[5])
            else:
                self.apiDict["pathVariable"] = apiList[5]
            if len(apiList[6]) != 0:
                self.apiDict["queryParameter"] = eval(apiList[6])
            else:
                self.apiDict["queryParameter"] = apiList[6]
            if len(apiList[7]) != 0:
                self.apiDict["body"] = eval(apiList[7])
            else:
                self.apiDict["body"] = apiList[7]
            if len(apiList[8]) != 0:
                self.apiDict["response"] = eval(apiList[8])
            else:
                self.apiDict["response"] = apiList[8]
        except Exception as e:
            print("exception: ", e)
            print("apiString: ", apiString)
            print("apiList: ", apiList)

        self.apiDict["section"] = "%s_%s"%(self.apiDict["http_method"], self.apiDict["path"])
        hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))
        headers = {"Accept": "application/json"}
        self.hostDict = hf.getAllItem(module)
        global DEBUG
        if self.hostDict["DEBUG"] == "True":
            DEBUG = True
        else:
            DEBUG = False
        if ("AUTH" in self.hostDict) and (self.hostDict["AUTH"].lower() == "yes"):
            # headers["access-token"] = self.hostDict["TOKEN"]
            if "BOOT" in module:
                headers["Authorization"] = self.hostDict["TOKEN"]
            else:
                headers["access-token"] = self.hostDict["TOKEN"]
        self.hostDict["headers"] = headers

class Excel(object):
    """docstring for Excel"""
    #formatting_info=True原样打开
    def __init__(self, file_name):
        self.file_name = file_name
        
    def read_sheet_names(self):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_names = table_obj.sheet_names()
        return sheet_names[4:]

    def get_sheet_index(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_names = table_obj.sheet_names()
        count = 0
        for item in sheet_names:
            if sheet_name == item:
                sheet_index = count
                break
            count = count + 1
            if count == len(sheet_names):
                return False, "Not Found tabel %s, Please Check it ~" %sheet_name
        return True, sheet_index

    def read_sheet_all_content(self, sheet_name): 
        table_obj = xlrd.open_workbook(self.file_name)
        content = table_obj.sheet_by_name(sheet_name)
        ord_list=[]
        for rownum in range(content.nrows):
            ord_list.append(content.row_values(rownum))
        #返回的类型是一个list
        return ord_list

    def read_sheet_content(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet_obj = table_obj.sheet_by_name(sheet_name)
        row_num = sheet_obj.nrows
        col_num = sheet_obj.ncols

        titles = sheet_obj.row_values(rowx=5)
        value_list = []
        value_list.append(titles)
        for row in range(6, row_num):
            values = sheet_obj.row_values(rowx=row)
            value_list.append(values)
        return value_list

    def get_case_info(self, sheet_name, case_num):
        cases = self.read_sheet_content(sheet_name)
        count = 0
        for case in cases:
            if case[0] == case_num:
                return True, case
            else:
                count = count + 1
            if count == len(cases):
                return False, "Not Fount %s Case, Please check it ~" %case_num

    def delete_excel_row(self, sheet_name, case_num):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        col_val = sheet.col_values(0)
        count = 0
        for item in col_val:
            if item == case_num:
                row_index = count
                break
            count = count + 1
            if count == len(col_val):
                return False, "Not Fount %s Case, Please Check it ~ " %case_num
        read_all = self.read_sheet_all_content(sheet_name)
        read_all.pop(row_index)
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        for m in range(len(read_all)):
            for n in range(len(read_all[m])):
                new_sheet.write(m, n, read_all[m][n])
        new_wb.save(self.file_name)
        return True, "Delete %s Success……" %case_num

    def modify_excel_row(self, sheet_name, case_info):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        col_val=sheet.col_values(0)#第一列的值
        count = 0
        for item in col_val:
            if item == case_info[0]:
                row_index = count
                break
            count = count + 1
            if count == len(col_val):
                return False, "Not Fount %s Case, Please Check it ~ " %case_info[0]
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        for i in range(len(case_info)):
            new_sheet.write(row_index, i, case_info[i])
        new_wb.save(self.file_name)
        return True, "Modify %s Success……" %case_info[0]

    def add_row_data(self, sheet_name, info_list):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        nrows = sheet.nrows
        new_wb = xl_copy(table_obj)  # 将原有的Excel，拷贝一个新的副本
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_sheet = new_wb.get_sheet(sheet_index) # 重新在新的Excel中获取
        for i in range(len(info_list)):
            new_sheet.write(nrows,i,info_list[i])
        new_wb.save(self.file_name)
        return True, 'Add %s Success……' %info_list[0]

    def delete_all_case(self, sheet_name):
        table_obj = xlrd.open_workbook(self.file_name)
        sheet = table_obj.sheet_by_name(sheet_name)
        read_all = self.read_sheet_all_content(sheet_name)
        length = len(read_all)
        if length > 6:
            for i in range(length-1, 5, -1):
                read_all.pop(i)
        status, sheet_index = self.get_sheet_index(sheet_name)
        if not status:
            return False, sheet_index
        new_wb = xl_copy(table_obj)
        new_sheet = new_wb.get_sheet(sheet_index)
        print("read_all: ", read_all)
        for m in range(len(read_all)):
            for n in range(len(read_all[m])):
                new_sheet.write(m, n, read_all[m][n])
        new_wb.save(self.file_name)
        return True, "Delete Data Success …… "

    def split_table(self, sheet_name):
        content = self.read_sheet_content(sheet_name)
        sheet_def = {"Sum_Up": "概览", "Host_Apply": "主机交付", "IDC_Mgmt": "数据中心", "Device_Mgmt": "设备管理", "Hardware_Mgmt": "硬件管理", "InstallOS_Mgmt": "装机管理", "Image_Mgmt": "镜像管理", "OOB_Mgmt": "带外管理", "Task_Mgmt": "任务管理", "Proxy_Mgmt": "分布式管理", "Asset_Mgmt": "资产管理", "ACL_Mgmt": "安全审计", "Report_Mgmt": "报表管理", "User_Mgmt": "用户管理", "System_Mgmt": "系统管理", "Notice_Mgmt": "通知中心", "Env_Config": "环境配置与日志", "Auth_Mgmt": "权限管理-UAM", "Data_Sync": "数据对接"}
        sheet_keys = sheet_def.keys()
        undef_list = []
        for items in content[6:]:
            count = 0
            for sheet_key in sheet_keys:
                case_id = items[0].upper()
                if case_id.startswith(sheet_key.upper()):
                    status, output = self.add_row_data(sheet_def[sheet_key], items)
                    break
                else:
                    count = count + 1
                if count == len(sheet_keys):
                    undef_list.append(items)
        status, output = self.delete_all_case(sheet_name)
        print(status, output)
        if len(undef_list) > 0:
            for items in undef_list:
                status, output = self.add_row_data(sheet_name, items)
                #print(status, output)
                #
    def modify_case_status(self, sheet_name, case_num, status):
        curTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        cases = self.read_sheet_content(sheet_name)
        count = 0
        if status:
            result = "PASS"
        else:
            result = "FAIL"
        for case_info in cases:
            if case_info[0] == case_num:
                case_info[12] = "Robot"
                case_info[13] = curTime
                case_info[14] = result
                status, oupput = self.modify_excel_row(sheet_name, case_info)
                return status, oupput
            else:
                count = count + 1
            if count == len(cases):
                return False, "Not Fount %s Case, Please check it ~" %case_num


        return True, "Split Case Info Succuss …… "

if __name__ == '__main__':
    print("common function and class")