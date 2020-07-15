#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Function: API Auto Test
# Usage: 
#     
# Author: JosingCai
# Email: 723266219@qq.com
# CreateDate: 2018/09/28
# Update: 10/07 

from local.function.comModVar import *
from local.function.base import *

def getApiStringList(module, mode="source"):
    if mode == "source":
        targetFN = "%s-API-Custom.csv"%module
        pathFN = "%s/local/%s/%s"%(curPath, CSVPath, targetFN)
        if not os.path.exists(pathFN):
            with open(pathFN, "w") as f:
                f.write("APIFunction|protocol|http_method|path|header|pathVariable|queryParameter|body|response\n")
            return []
        with open(pathFN) as f:
            content = f.read()
    elif mode == "result":
        targetFN = "%s-TestReport.csv"%module
        pathFN = "%s/local/%s/%s"%(curPath, LogPath, targetFN)
        if not os.path.exists(pathFN):
            return []
        with open(pathFN) as f:
            content = f.read()
    strList = []
    apiStringList = content.split("\n")
    for String in apiStringList[1:]:
        if len(String) != 0:
            strList.append(String)
    return strList

def getSpecApi(module, method_API):
    strList = getApiStringList(module, mode="source")
    count = 0
    for apiString in strList:
        tmpApi = apiString.split("|")
        if DEBUG:
            print("%s:%s_%s"%(method_API, tmpApi[2], tmpApi[3]))
        if method_API == "%s_%s"%(tmpApi[2], tmpApi[3]):
            return True, apiString
        else:
            count = count + 1
        if count == len(strList):
            output = "Not Get Source Info in %s-API-Custom.csv, Please Add it ~ "%module
            return False, output

class API(RawAPI):
    """docstring for API"""
    def __init__(self, module, apiString):
        #RawAPI.__init__(self, apiString)
        super(API, self).__init__(module, apiString)
        self.module = module
        self.config = "%s-API-Dependancy.ini"%self.module
        self.saveResult = "%s-API-Result.ini"%self.module
        self.logFile = "%s-API-%s.log"%(self.module, today)
        self.testReport = "%s-TestReport.csv"%(self.module)
        self.cf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, self.config))
        self.hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))
        self.sf = localConfigParser("%s/local/%s/%s"%(curPath,configPath, self.saveResult))
        beforeCase = self.cf.getOption(self.apiDict["section"], "beforeCase")
        afterCase = self.cf.getOption(self.apiDict["section"], "afterCase")
        runNum = self.cf.getOption(self.apiDict["section"], "runNum")
        param_def = self.cf.getOption(self.apiDict["section"], "param_def")
        self.depIDs = []
        if beforeCase:
            self.depIDs = eval(beforeCase)
        self.chkIDs = []
        if afterCase:
            self.chkIDs = eval(afterCase)
        self.runNum = 1
        if runNum:
            self.runNum = eval(runNum)
        self.param_def = []
        if param_def:
            self.param_def = eval(param_def)
    
    def expectAPI(self):
        if self.runNum == 0:
            if DEBUG:
                print("%s has 0 runNum test ..."%self.apiDict["section"])
            response = {"status": "untested", "message": "未测试"}
            url = self.getRawUrl()
            data = ""
            self.saveTestReport(url, data, response)
            return True, "%s has 0 runNum test ..."%self.apiDict["section"]
        return False, "Common Test"

    def hadRun(self):
        if self.sf.hasSection(self.apiDict["section"]):
            return True, "%s had already Test ... "%self.apiDict["section"]

    def getRawUrl(self):
        if len(self.hostDict["PREPATH"]) != 0:
            tmpPath = "%s%s"%(self.hostDict["PREPATH"], self.apiDict["path"])
            url = "%s://%s%s"%(self.hostDict["PROTOCOL"], self.hostDict["IP"], tmpPath)
        else:
            url = "%s://%s%s"%(self.hostDict["PROTOCOL"], self.hostDict["IP"], self.apiDict["path"])
        return url

    def getDepVars(self):
        depOutVars = {}
        self.sf = localConfigParser("%s/local/%s/%s"%(curPath,configPath, self.saveResult))
        if self.depIDs and len(self.depIDs) != 0:
            for depID in self.depIDs:
                outVars = self.sf.getOption(depID, "outVars")
                if outVars and len(outVars) != 0:
                    depOutVars.update(eval(outVars))
        # depOutVars = self.cf.getAllItem("common")
        for item in self.param_def:
            ret = self.cf.getOption("common", item)
            if ret:
                def_vars = self.cf.getOption("common", item)
                if def_vars:
                    depOutVars.update(eval(def_vars))
        if DEBUG:
            print("depOutVars: ", depOutVars)
        return depOutVars

    def getRandomStr(self, randomlength=16):
        randomStr = ''
        baseStr = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(baseStr) - 1
        for i in range(randomlength):
            randomStr += baseStr[random.randint(0, length)]
        return randomStr

    def getAbDef(self, Type):
        valueList = []
        if Type == "int" or Type == "integer":
            valueList = [1-2**16, 1-2**8, -1, 0, 2**8-1, 2**16-1]
        elif Type == "string":
            specStr = '~!@#$%^&*()_+=|[]{}<>,.?/"'
            str255 = getRandomStr(255)
            str256 = getRandomStr(256)
            str257 = getRandomStr(257)
            valueList = [str255, str256, str257, specStr]
        return valueList

    def getArray(self, *items):
        maxLen = len(items[0])
        for item in items:
            if len(item) > maxLen:
                maxLen = len(item)
        productList = []
        list0 = [0]
        arrayList = []
        for item in items:
            tmpList = []
            if len(item) < maxLen:
                tmpList = list0*(maxLen-len(item)) + item
                productList.append(tmpList)
            else:
                productList.append(item)
        for item in product(*productList):
            arrayList.append(item)
        return arrayList

    def getUrlPath(self, url, **depOutVars):
        urlList = []
        if len(self.apiDict["pathVariable"]) != 0:
            Keys = self.apiDict["pathVariable"].keys()
            for Key in Keys:
                if DEBUG:
                    print("Key: ", Key)
                if Key not in depOutVars:
                    keyVar = self.cf.getOption("common", Key)
                    if not keyVar:
                        String = "Not Define Var: %s"%(Key)
                        if DEBUG:
                            print(String)
                        return False, String
                    else:
                        depOutVars[Key] = eval(keyVar)
                        if isinstance(depOutVars[Key], list):
                            for index in range(len(depOutVars[Key])):
                                value = depOutVars[Key][index]
                                URL = url.replace("{%s}"%Key, str(value))
                                urlList.append(URL)
                        else:
                            URL = url.replace("{%s}"%Key, str(depOutVars[Key]))
                            urlList.append(URL)
                else:
                    if isinstance(depOutVars[Key], list):
                        for index in range(len(depOutVars[Key])):
                            value = depOutVars[Key][index]
                            URL = url.replace("{%s}"%Key, str(value))
                            urlList.append(URL)
                    else:
                        URL = url.replace("{%s}"%Key, str(depOutVars[Key]))
                        urlList.append(URL)
        else:
            urlList.append(url)
        return True, urlList

    def getQueryStr(self, dep_mode="no", **depOutVars):
        queryStrList = []
        multi_no_list = ["page", "page_size"]
        if len(self.apiDict["queryParameter"]) != 0:
            commonVars = self.cf.getAllItem("common")
            uniVars = self.cf.getOption("common", "uniVar")
            Keys = self.apiDict["queryParameter"].keys()
            keyList = []
            productList = []
            if DEBUG:
                print("Keys: ", Keys)
            for Key in Keys:
                if self.apiDict["queryParameter"][Key] == "string":
                    if Key in depOutVars:
                        depOutVars[Key] = ["", " "] + depOutVars[Key]
                    elif Key in commonVars:
                        depOutVars[Key] = ["", " "] + commonVars[Key]
                    else:
                        depOutVars[Key] = ["", " "]
                elif self.apiDict["queryParameter"][Key] == "integer":
                    if Key in depOutVars:
                        depOutVars[Key] = [-1, 65536] + depOutVars[Key]
                    elif Key in commonVars:
                        depOutVars[Key] = [-1, 65536] + commonVars[Key]
                    else:
                        depOutVars[Key] = [-1, 65536]

                if "SEARCH" in self.hostDict and self.hostDict["SEARCH"]=="Multi" and dep_mode!="yes":
                    if DEBUG:
                        print("Case ID: ", self.apiDict["section"])
                    if isinstance(depOutVars[Key], list):
                        if Key in multi_no_list:
                            continue
                        if len(depOutVars[Key]) > 2:
                            rep_length = 2
                            repeat_list = random.sample(depOutVars[Key], rep_length)
                            if DEBUG:
                                print("More Value: ", depOutVars[Key])
                        else:
                            rep_length = len(depOutVars[Key])
                            repeat_list = depOutVars[Key]
                        multi_list = list(product(repeat_list,repeat=rep_length))
                        keyList.append(Key)
                        multi_info = []
                        if DEBUG:
                            print("multi_list: ", multi_list)
                        for info in multi_list:
                            info = list(set(info))
                            info = map(str,info)
                            value = ','.join(info)
                            multi_info.append(value)
                            queryString = Key + "=" + value
                            queryStrList.append(queryString)
                        productList.append(multi_info)
                else:
                    if isinstance(depOutVars[Key], list):
                        keyList.append(Key)
                        productList.append(depOutVars[Key])
                        for item in depOutVars[Key]:
                            queryString = Key + "=" + str(item)
                            queryStrList.append(queryString)
                    else:
                        queryString = Key + "=" + str(depOutVars[Key])
                        queryStrList.append(queryString)
            if DEBUG:
                print("productList length: ", len(productList))
                print("keyList length: ", len(keyList))

            if len(productList) > 6:
                if DEBUG:
                    print("More Value: ", productList)
                    print("More Key : ", keyList)
                #productList = random.sample(productList,6)
                productList = productList[:6]
                keyList = keyList[:6]
                
            arrayList = []
            for item in product(*productList):
                arrayList.append(item)
            for info in arrayList:
                String = ""
                for i in range(len(keyList)):
                    #print("i: ", i)
                    if info[i] != 0:
                        if len(String) == 0:
                            String = keyList[i] + "=" + str(info[i])
                        else:
                            String = String + "&" + keyList[i] + "=" + str(info[i])
                queryStrList.append(String)
        if DEBUG:
            print("queryStrList: ", queryStrList)
            print("queryStrList length: ", len(queryStrList))

        return True, queryStrList

    def chkUniVar(self, name):
        ret = self.cf.getOption("common", "uniVar")
        if DEBUG:
            print("uniVar: ", ret)
        if not ret:
            return False
        else:
            for value in eval(ret):
                if name.strip() == value.strip():
                    return True
            return False

    def getBody(self, **depOutVars):
        bodyList = []
        ramStr12 = self.getRandomStr(12)
        ramStr8 = self.getRandomStr(8)
        curTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        defDict = {"description": "auto-%s"%self.apiDict["APIFunction"], "pid": 0, "tenantId": "default", \
        "remark": "auto %s remark"%self.apiDict["APIFunction"], "name": "auto-%s"%ramStr8, \
        "number": "auto-%s"%ramStr8, "date": curTime, "acquire_time": curTime, \
        "started_at": curTime, "onshelve_at": curTime, "fixed_asset_number": ramStr12, "sn": ramStr12}
        if len(self.apiDict["body"]) != 0:
            commonVars = self.cf.getAllItem("common")
            Keys = self.apiDict["body"].keys()
            count = 0
            keyList = []
            uniVar = self.cf.getOption("common", "uniVar")
            for Key in Keys:
                if self.apiDict["body"][Key] == "array":
                    if Key in commonVars:
                        self.apiDict["body"][Key] = commonVars[Key]
                    if Key in depOutVars:
                        self.apiDict["body"][Key] = depOutVars[Key]
                    if self.apiDict["body"][Key] == "array":
                        return False, "Not Define Var: %s"%(Key)
                else:
                    if Key in depOutVars and isinstance(depOutVars[Key], list):
                        keyList.append(Key)
                        if self.apiDict["body"][Key] == "string":
                            abnormal_list = ["", " "]
                            depOutVars[Key] = abnormal_list + depOutVars[Key]
                        elif self.apiDict["body"][Key] == "integer":
                            abnormal_list = [-1, 65536]
                            depOutVars[Key] = abnormal_list + depOutVars[Key]
                        continue
                    elif Key in depOutVars:
                        self.apiDict["body"][Key] = depOutVars[Key]
                        continue

                    if Key in commonVars and isinstance(commonVars[Key], list):
                        keyList.append(Key)
                        depOutVars[Key] = eval(self.cf.getOption("common", Key))
                        continue
                    elif Key in commonVars:
                        self.apiDict["body"][Key] = commonVars[Key]
                        continue

                    if Key in defDict:
                        self.apiDict["body"][Key] = defDict[Key]
                        continue
                    if self.apiDict["body"][Key] == "string":
                        keyList.append(Key)
                        depOutVars[Key] = [ramStr8, " ", ""]
                        #self.apiDict["body"][Key] = ramStr8
                    elif Key == "id" and self.apiDict["http_method"] == "post":
                        apiDict["body"][Key] = 0
                        continue
                    elif self.apiDict["body"][Key] == "integer":
                        keyList.append(Key)
                        depOutVars[Key] = [-1, 65536]
                        # return False, "Not Define Var: %s"%(Key)
            forList = []
            productList = []
            for Key in keyList:
                productList.append(depOutVars[Key])
            #print "productList: ", productList
            for items in product(*productList):
                forList.append(items)
            #print "forList: ", forList
            for j in range(len(forList)):
                infoDict = {}
                for Key in self.apiDict["body"].keys():
                    ret = self.chkUniVar(Key)
                    if ret:
                        infoDict[Key] = "auto%s"%self.getRandomStr(8)
                        #print("%s: %s"%(Key, infoDict[Key]))
                    else:
                        infoDict[Key] = self.apiDict["body"][Key]
                for i in range(len(keyList)):
                    Key = keyList[i]
                    Value = forList[j][i]
                    infoDict[Key] = Value
                #print("infoDict: ", infoDict)
                bodyList.append(infoDict)
        return True, bodyList

    def assembleData(self, dep_mode="no"):
        url = self.getRawUrl()
        depOutVars = self.getDepVars()
        if DEBUG:
            print("%s depOutVars: %s"%(self.apiDict["section"], depOutVars))
        status, urlList = self.getUrlPath(url, **depOutVars)
        if not status:
            return status, urlList
        if self.apiDict["http_method"] == "get" and dep_mode == "yes":
            reqDict = {}
            if len(urlList) > 0:
                reqDict["url"] = urlList[0]
                reqDict["body"] = ""
                return True, [reqDict]
            else:
                reqDict["url"] = ""
                reqDict["body"] = ""
                return False, "No Dep Data"
        status, queryList = self.getQueryStr(dep_mode=dep_mode,**depOutVars)
        if not status:
            return status, queryList
        status, bodyList = self.getBody(**depOutVars)
        if not status:
            return status, bodyList
        reqList = []
        tmpList = []
        productList = [urlList]
        if len(queryList) != 0:
            productList.append(queryList)
        if len(bodyList) != 0:
            productList.append(bodyList)
        for items in product(*productList):
            tmpList.append(items)
        if len(tmpList) == 0:
            return False, depOutVars
        length = len(tmpList[0])
        for items in tmpList:
            reqDict = {}
            if length == 1:
                reqDict["url"] = items[0]
                reqDict["body"] = ""
            elif length == 3:
                url = items[0] + "?" + items[1]
                reqDict["url"] = url
                reqDict["body"] = items[2]
            elif length == 2:
                if self.apiDict["http_method"] == "get": 
                    url = items[0] + "?" + items[1]
                    reqDict["url"] = url
                    reqDict["body"] = ""
                else:
                    reqDict["url"] = items[0]
                    reqDict["body"] = items[1]
            reqList.append(reqDict)
        return True, reqList

    def runMethod(self, url, data):
        if self.apiDict["http_method"] == "get":
            resp = requests.get(url, headers=self.hostDict["headers"], json=None, verify=False)
        elif self.apiDict["http_method"] == "post":
            resp = requests.post(url, headers=self.hostDict["headers"], json=data, verify=False)
        elif self.apiDict["http_method"] == "put":
            resp = requests.put(url, headers=self.hostDict["headers"], json=data, verify=False)
        elif self.apiDict["http_method"] == "delete":
            resp = requests.delete(url, headers=self.hostDict["headers"], json=None, verify=False)
        curTime=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        with open("%s/local/%s/%s"%(curPath, LogPath, self.logFile), "a+") as f:
            f.write("[ %s ]\n"%curTime)
            f.write("%s: %s\n"%(self.apiDict["http_method"], url))
            f.write("headers: %s\n"%(self.hostDict["headers"]))
            if data:
                f.write("request: %s\n"%data)
                self.sf.writeSection(self.apiDict["section"], "requestVars", data)
            f.write("response: %s"%resp.content)
        if not resp.ok:
            try:
                info = resp.json()
                if DEBUG:
                    print("response: ", info)
                response = {"status": info["status"], "message": "执行失败", "failReason": info["message"]}
            except Exception as e:
                print("runMethod 1 exception: ", e)
                response = {"status": "failure", "message": "执行失败", "failReason": resp.content}
            return False, response
        try:
            response = resp.json()
        except Exception as e:
            print("runMethod 2 exception: ", e)
            response = {"status": "success", "message": "执行成功", "failReason": " "}
        if "status" not in response:
            response.update({"status": "success", "message": "执行成功", "failReason": " "})
        else:
            response.update({"failReason": " "})
        return True, response
    
    def saveTestReport(self, url, data, response):
        TestTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        isExist = os.path.exists("%s/local/%s/%s"%(curPath, LogPath, self.testReport))
        if "content" not in response:
            response["content"] = ""
        if not isExist:
            tableHeader = "APIFunction|http_method|path|url|body|TestTime|TestResult|TestContent|FailReason"
            with open("%s/local/%s/%s"%(curPath, LogPath, self.testReport), "w+") as fp:
                fp.write("%s\n"%tableHeader)
        with open("%s/local/%s/%s"%(curPath, LogPath, self.testReport), "a+") as fp:
            rString = self.apiDict["APIFunction"] + "|" + self.apiDict["http_method"] + "|" + self.apiDict["path"] + "|" + url + "|" + str(data) + "|" + TestTime + "|" + response['status']
            if "failReason" not in response:
                response["failReason"] = ""
            else:
                response["failReason"] = str(response["failReason"]).replace("\n", "")
            if "content" not in response:
                response["content"] = ""
            else:
                if isinstance(response["content"], str):
                    response["content"] = str(response["content"]).replace("\n", "")
            rString = rString + "|" + response['failReason'] + "|" + str(response['content'])
            fp.write("%s\n"%rString)
        return True

    def saveOutVar(self, response):
        outVarsDict = {}
        outVars = self.cf.getOption( self.apiDict["section"], "outVars")
        if DEBUG:
            print("outVars: ", outVars)
        if outVars is False:
            return True, "No Special Out Vars"
        outVarItems = eval(outVars)
        Keys = outVarItems.keys()
        for Key in Keys:
            tmp = response
            if "-" in outVarItems[Key]:
                items = outVarItems[Key].split("-")
                values = []
                for item in items:
                    if "*" in item:
                        subItems = item.split("*")
                        for index in range(len(tmp[subItems[0]])):
                            value = tmp[subItems[0]][index][subItems[1]]
                            values.append(value)
                        tmp = values
                    else:
                        if isinstance(tmp, list):
                            subValues = []
                            for index in range(len(tmp)):
                                subValues.append(tmp[index][item])
                            tmp = subValues
                        else:
                            tmp = tmp[item]
            else:
                tmp = tmp[outVarItems[Key]]
            if isinstance(tmp, list):
                items = []
                for item in tmp:
                    if isinstance(item, int):
                        items.append(item)
                    else:
                        if len(item) == 0:
                            continue
                        if len(item) == 1 and isinstance(item, list) and len(item[0]) == 0:
                            continue
                        try:
                            if isinstance(item, list):
                                items.append(item)
                            else:
                                items.append(item)
                        except Exception as e:
                            print("saveOutVar exception: ", e)
                outVarsDict[Key] = items
            else:
                if isinstance(tmp, int):
                    outVarsDict[Key] = tmp
                else:
                    outVarsDict[Key] = tmp
        self.sf.writeSection(self.apiDict["section"], "outVars", outVarsDict)
        return True, "Get Vars to Output Success"

    def chkItem(self, reqDict, chkDict):
        noChkVars = self.cf.getOption("common", "noChkVar")
        passList = []
        cmpDict = {}
        chkVars = {}
        flag = "pass"
        chkVars = self.cf.getOption(self.apiDict["section"], "chkVars")
        chkInfo = chkDict["content"]
        if not isinstance(chkInfo, dict):
            return True, "No need Check"
        if chkVars:
            chkVars = eval(chkVars)
        else:
            chkVars = {}
        if len(chkVars) != 0:
            Keys = chkVars.keys()
            for Key in Keys:
                tmp = chkDict
                if "-" in chkVars[Key]:
                    items = chkVars[Key].split("-")
                    values = []
                    for item in items:
                        try:
                            if "*" in item:
                                subItems = item.split("*")
                                for index in range(len(tmp[subItems[0]])):
                                    value = tmp[subItems[0]][index][subItems[1]]
                                    values.append(value)
                                tmp = values
                            else:
                                tmp = tmp[item]
                        except Exception as e:
                            print("chkItem 1 exception: ", e)
                            tmp = "Not Found Var: %s"%item

                if isinstance(tmp, list):
                    values = []
                    for item in tmp:
                        if isinstance(item, int):
                            items.append(item)
                        else:
                            try:
                                items.append(item.encode("utf-8"))
                            except Exception as e:
                                print("chkItem 2 exception: ", e)
                                items.append("")
                    chkVars[Key] = items
                else:
                    if isinstance(tmp, int):
                        chkVars[Key] = tmp
                    else:
                        try:
                            chkVars[Key] = tmp.encode("utf-8") 
                        except Exception as e:
                            print("chkItem 3 exception: ", e)
                            chkVars[Key] = tmp

            chkInfo.update(chkVars)

        Keys = reqDict.keys() 
        if DEBUG:
            print("reqDict: ", reqDict)
        for Key in Keys:
            print(Key)
            print(noChkVars)
            if Key not in noChkVars:
                if Key not in chkInfo:
                    cmpDict[Key] = "Actual: , Expected: %s"%(reqDict[Key])
                    flag = "false"
                if isinstance(reqDict[Key], list):
                    if len(list(set(reqDict[Key]).difference(set(chkInfo[Key])))) != 0:
                        cmpDict[Key] = "Actual: %s, Expected: %s"%(chkInfo[Key], reqDict[Key])
                        flag = "false"
                elif reqDict[Key] != chkInfo[Key]:
                    cmpDict[Key] = "Actual: %s, Expected: %s"%(chkInfo[Key], reqDict[Key])
                    flag = "false"
                else:
                    passList.append(Key)
        if DEBUG:
            print("passList: ", passList)
        return flag, cmpDict

    def analysisReponse(self, url, data, response):
        if not self.saveTestReport(url, data, response):
            print("Save Test Result Failed ... ")
        if  response["status"] != "success":
            self.sf.writeSection(self.apiDict["section"], "result", "FAIL")
            return False, response['failReason']
        else:
            self.sf.writeSection(self.apiDict["section"], "result", "PASS")
            status, output = self.saveOutVar(response)
            return True, output

    def run_sql_inject(self, url):
        sql_inject_tmp_log_path = "local/LOG/SQL_INJECT_tmp.log"
        sql_inject_tool_path = "tools/sqlmap"
        cookie = self.hostDict["COOKIE"]
        if self.apiDict["http_method"] == "get":
            if "?" in url:
                url = url.split("?")[0]
            if len(self.apiDict["queryParameter"]) > 0:
                count = 0 
                for Key in self.apiDict["queryParameter"].keys():
                    if count == 0:
                        url = url + "?" + Key + "=" + self.apiDict["queryParameter"][Key]
                    else:
                        url = url + "&" + Key + "=" + self.apiDict["queryParameter"][Key]
                    count = count + 1
            cmd = '%s/sqlmap.py -u "%s" --level 1 --method %s --cookie "%s" --dbs' %(sql_inject_tool_path, url, self.apiDict["http_method"],cookie)
        else:
            cmd = '%s/sqlmap.py -u "%s" --level 1 --method %s --data \"%s\" --cookie "%s" --dbs' %(sql_inject_tool_path, url, self.apiDict["http_method"],self.apiDict["body"], cookie)
        fd = open(sql_inject_tmp_log_path, "w")
        fd.write("cmd: %s" %cmd)
        p = pexpect.spawn(cmd, timeout=30, maxread=4096, encoding='utf-8', logfile = fd)
        startTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        for i in range(4):
            p.waitnoecho(timeout=10)
            p.sendline("Y")
        p.expect(pexpect.EOF,  timeout=None)
        endTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        fd.close()
        sql_inject_log_path = "local/LOG/SQL_INJECT_%s.log" % today
        with open(sql_inject_tmp_log_path) as f:
            content = f.read()
        with open(sql_inject_log_path, "a+") as fd:
            fd.write("startTime: %s\n" %startTime)
            fd.write(content)
            fd.write("endTime: %s\n" %endTime)
        return True

def threadRun(handle, url, body):
    retDict = {}
    retDict["case_id"] = handle.apiDict["section"]
    retDict["url"] = url
    retDict["body"] =  body
    retDict["header"] = handle.hostDict["headers"]
    status, response = handle.runMethod(url, body)
    retDict["response"] = response
    retDict["failReason"] = "%s: %s"%(response["message"], response["failReason"])
    retDict["testResult"] = response["status"]
    status, output = handle.analysisReponse(url, body, response)
    return status, retDict

def runAPI(module, apiString, number=1, mode="single", chkMode="no", dep_mode="no"):
    # 依赖用例chkMode置为no, 只执行beforeCase, afterCase不执行
    api = API(module, apiString)
    if "SQLINJECT" in api.hostDict and api.hostDict["SQLINJECT"] == "yes":
        url_raw = api.getRawUrl()
        api.run_sql_inject(url_raw)
        retDict = {}
        retDict["case_id"] = api.apiDict["section"]
        retDict["response"] = "SQL Inject Run Succuss"
        return True, [retDict]

    if api.runNum != 0 and api.runNum != 1:
        number = api.runNum

    status, output = api.expectAPI()
    if status:
        retDict = {}
        retDict["case_id"] = api.apiDict["section"]
        retDict["response"] = output
        return status, [retDict]

    if api.depIDs:
        for depID in api.depIDs:
            retDict = {}
            retDict["case_id"] = api.apiDict["section"]
            apiString = api.cf.getOption(depID, "raw")
            if not apiString:
                retDict["response"] = "Not Get Raw Info for Test"
                return False, [retDict]
            status, outputList = runAPI(module, apiString, number=1, mode="single", chkMode="no")
            if not status:
                return status, outputList

    if mode == "single":
        status, reqList = api.assembleData(dep_mode="yes")
        reqList = [reqList[0]]
    elif number != 1:
        status, reqList = api.assembleData(dep_mode="yes")
        if len(reqList) < number:
            loopNum = int(number/len(reqList)) + 1
            for i in range(loopNum):
                status, tmpList = api.assembleData()
                reqList = reqList + tmpList
        #reqList = reqList[:number]
        if DEBUG:
            print("Init List: ", reqList[:40])
        reqList = random.sample(reqList, number)
        if DEBUG:
            print("Run List: ", reqList)
        #return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    else:
        status, reqList = api.assembleData()
    if not status:
        return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    
    if DEBUG:
        print("reqList: ", reqList)
    resultList = []
    if (len(api.chkIDs) != 0 or chkMode == "no") and mode != "single":
        chkID = ""
        delID = ""    

        for case_id in api.chkIDs:
            if case_id.startswith("get"):
                chkID = case_id
            elif case_id.startswith("delete"):
                delID = case_id    

        for info in reqList:
            retDict = {}
            retDict["case_id"] = api.apiDict["section"]
            retDict["url"] = info['url']
            retDict["body"] =  info['body']
            retDict["header"] = api.hostDict["headers"]
            status, response = api.runMethod(info['url'], info['body'])
            if not status:
                retDict["response"] = response["failReason"]
                retDict["failReason"] = response["message"]
                retDict["testResult"] = response["status"]
                resultList.append(retDict)
                return False, resultList
            status, output = api.analysisReponse(info['url'], info['body'], response)
            retDict["response"] = output
            if not status:
                resultList.append(retDict)
                return False, resultList    
            if chkID.strip():
                chkDict = {}
                chkDict["case_id"] = chkID
                status, apiString = getSpecApi(module, chkID)
                if not status:
                    chkDict["response"] = apiString
                    resultList.append(chkDict)
                    return False, resultList
                chkApi = API(module, apiString)
                status, chkList = chkApi.assembleData()
                if not status:
                    chkDict["response"] = chkList
                    resultList.append(chkDict)
                    return False, resultList
                status, chkDict = threadRun(chkApi, chkList[0]["url"], chkList[0]["body"])
                resultList.append(chkDict)
                if not status:
                    return False, [chkDict]
                if api.apiDict["section"].startswith("delete"):
                    retDict["testResult"] = "pass"
                    retDict["failReason"] = ""
                else:
                    flag, failList = chkApi.chkItem(info['body'], chkDict["response"])
                    retDict["testResult"] = flag
                    retDict["failReason"] = failList    

            if delID.strip():
                delDict = {}
                delDict["case_id"] = delID
                status, apiString = getSpecApi(module, delID)
                if not status:
                    delDict["response"] = apiString
                    resultList.append(delDict)
                    return False, resultList
                delApi = API(module, apiString)
                status, delList = delApi.assembleData()
                if not status:
                    delDict["response"] = delList
                    resultList.append(delDict)
                    return False, resultList
                status, delDict = threadRun(delApi, delList[0]["url"], delList[0]["body"])
                resultList.append(delDict)
                if not status:
                    return False, [delDict]
            resultList.append(retDict)
    else:
        # if "SQLINJECT" in api.hostDict and api.hostDict["SQLINJECT"] == "yes":
        #         print("SQL Inject……")
        #         api.run_sql_inject(reqList[0]["url"])
        #         retDict = {}
        #         retDict["case_id"] = api.apiDict["section"]
        #         retDict["response"] = "SQL Inject Run Succuss"
        #         return True, [retDict]
        if api.hostDict["THREADING"] == "False":
            for info in reqList:
                status, retDict = threadRun(api, info["url"], info["body"])
                resultList.append(retDict)
        else:
            threads = []
            length = len(reqList)
            for i in range(length):
                t = MyThread(threadRun, (api, reqList[i]["url"], reqList[i]["body"]))
                threads.append(t)
            for i in range(length):
                threads[i].start()
            for i in range(length):
                threads[i].join()
                status, retDict = threads[i].get_result()
                resultList.append(retDict)
    return True, resultList

def runTargetAPI(module, method_API, number=1, mode="loop"):
    # status, apiString = getSpecApi(module, method_API)
    # if DEBUG:
    #     print("apiString: ", apiString)
    # if not status:
    #     return False, [{"case_id": method_API, "response": apiString}]
    config = "%s-API-Dependancy.ini"%module
    cf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, config))
    apiString = cf.getOption(method_API, "raw")
    if not apiString:
        return False, [{"case_id": method_API, "response": "Get API raw info failed, Please Check it ~ "}]
    status, output = runAPI(module, apiString, number, mode, chkMode="yes")
    if not status:
        if DEBUG:
            print("run output: ", output)
    return True, output

def runAPIs(module):
    apiStringList = getApiStringList(module)
    resultList = []
    for apiString in apiStringList:
        if DEBUG:
            print(apiString)
        if len(apiString) == 0:
            continue
        apiInfo = apiString.split("|")
        case_id = "%s_%s"%(apiInfo[2], apiInfo[3])
        status, loopList = runTargetAPI(module, case_id, mode="loop")
        resultList = resultList + loopList
    TRFN = "%s/local/%s/%s-TestReport-%s.csv"%(curPath, LogPath, module, today)
    humanReadable(TRFN)
    return resultList

class RunCase(object):
    """docstring for RunCase"""
    def __init__(self, project):
        self.project = project.upper()
        rConfig = "%s-API-Result.ini"%self.project
        config = "%s-API-Dependancy.ini"%self.project
        tConfig = "%s-TestReport.csv"%self.project
        self.rfileName = "%s/local/%s/%s"%(curPath, configPath, rConfig)
        self.cfileName = "%s/local/%s/%s"%(curPath, configPath, config)
        self.rf = localConfigParser(self.rfileName)
        self.cf = localConfigParser(self.cfileName)
        self.tfileName = "%s/local/%s/%s"%(curPath, LogPath, tConfig)

    def run(self, **info):
        case_id = list(info.keys())[0]
        status, retList = runTargetAPI(self.project, case_id, mode="loop")
        if not status:
            return retList
        return retList

    def runAll(self):
        items = self.cf.getAllItem("common")
        curTime = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        if os.path.exists(self.tfileName):
            cmd = "mv %s %s_%s.bak"%(self.tfileName, self.tfileName, curTime)
            status, output = commands.getstatusoutput(cmd)
            if status != 0:
                print("output: ", output)
                return "Back up %s Failed: %s"%(self.rfileName, output)
        # rf = localConfigParser(self.rfileName)
        # for item in items.keys():
        #     rf.writeSection("common", item, items[item])
        return runAPIs(self.project)

class Case(object):
    def __init__(self, project):
        self.project = project.upper()
        cConfig = "%s-API-Dependancy.ini"%self.project
        rConfig = "%s-API-Result.ini"%self.project
        lConfig = "%s-TestReport.csv"%self.project
        self.cfileName = "%s/local/%s/%s"%(curPath, configPath, cConfig)
        self.rfileName = "%s/local/%s/%s"%(curPath, configPath, rConfig)
        self.lfileName = "%s/local/%s/%s"%(curPath, configPath, lConfig)
        if not os.path.exists(self.cfileName):
            f = open(self.cfileName, 'w')
            f.close()
        if not os.path.exists(self.rfileName):
            f = open(self.rfileName, 'w')
            f.close() 
        self.cf = localConfigParser(self.cfileName)
        self.rf = localConfigParser(self.rfileName)

    def getCaseDetail(self, case_id):
        infoDict = {}
        cContent =  self.cf.getSection(case_id)
        rContent =  self.rf.getSection(case_id)
        if cContent is False:
            cContent = {}
            cContent["beforeCase"] = " "
            cContent["outVars"] = " "
            cContent["chkVars"] = " "
            cContent["afterCase"] = " "
        if rContent is False:
            rContent = {}
            rContent["requestVars"] = " "
            rContent["outVarsTest"] = " "
            rContent["result"] = " "
        infoDict = cContent
        infoDict["case_id"] = case_id
        if "requestVars" in rContent:
            infoDict["requestVars"] = rContent["requestVars"]
        else:
            infoDict["requestVars"] = " "
        if "outVars" in rContent:
            infoDict["outVarsTest"] = rContent["outVars"]
        else:
            infoDict["outVarsTest"] = " "
        if "result" in rContent:
            infoDict["result"] = rContent["result"]
        else:
            infoDict["result"] = " "
        return infoDict

    def getCase(self, **info):
        if len(info) == 0:
            sections = self.cf.getAllSection()
            infoList = []
            for section in sections:
                if section == "common":
                    continue
                ret = self.getCaseDetail(section)
                if ret is False:
                    continue
                infoList.append(ret)
            return infoList
        Keys = list(info.keys())
        case_id = Keys[0]
        infoDict = self.getCaseDetail(case_id)
        return [infoDict]

    def delCase(self, case_id):
        status, output = self.cf.removeSection(case_id)
        if status is False:
            return output
        status, output = self.rf.removeSection(case_id)
        if status is False:
            return output
        return "Remove %s Config Info Success ~ "%case_id

    def getCaseDep(self, **info):
        if DEBUG:
            print(info)
        if len(info) != 0:
            section = list(info.keys())[0]
            ret = self.getCaseDetail(section)
            return [ret]
        sections = self.cf.getAllSection()
        infoList = []
        for section in sections:
            if section == "common":
                continue
            ret = self.getCaseDetail(section)
            if ret is False:
                continue
            infoList.append(ret)
        return infoList

    def postCaseDep(self, **info):
        section = info["case_id"]
        if len(section) == 0:
            return "Please Input Case ID "
        for option in info.keys():
            if option == "modify" or option == "case_id":
                continue
            value = info[option].strip()
            self.cf.writeSection(section, option, value)
        return "Add %s Success "%section

    def syncCaseDep(self):
        sHandle = Source(self.project)
        infoList = sHandle.getSConfig()
        sections = self.cf.getAllSection()
        for info in infoList:
            case_id = "%s_%s"%(info["http_method"], info["path"])
            count = 0 
            if len(sections) == 0:
                self.cf.writeSection(case_id, "beforeCase", "[]")
                self.cf.writeSection(case_id, "outVars", "{}")
                self.cf.writeSection(case_id, "chkVars", "{}")
                self.cf.writeSection(case_id, "afterCase", "[]")
                self.cf.writeSection(case_id, "runNum", "1")
                #self.cf.writeSection(case_id, "param_def", '["%s"]' %info["path"])
                self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])
            else:
                for section in sections:
                    if case_id == section:
                        if not self.cf.getOption(case_id,"beforeCase"):
                            self.cf.writeSection(case_id, "beforeCase", "[]")
                        if not self.cf.getOption(case_id,"outVars"):
                            self.cf.writeSection(case_id, "outVars", "{}")
                        if not self.cf.getOption(case_id,"chkVars"):
                            self.cf.writeSection(case_id, "chkVars", "{}")
                        if not self.cf.getOption(case_id,"afterCase"):
                            self.cf.writeSection(case_id, "afterCase", "[]")
                        if not self.cf.getOption(case_id,"runNum"):
                            self.cf.writeSection(case_id, "runNum", "1")
                        if not self.cf.getOption(case_id,"param_def"):
                            #self.cf.writeSection(info["case_id"], "param_def", '["%s"]' %info["path"])
                            self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                        if not self.cf.getOption(case_id,"raw"):
                            self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])
                        break
                    else:
                        count = count + 1
                    if count == len(sections):
                        self.cf.writeSection(case_id, "beforeCase", "[]")
                        self.cf.writeSection(case_id, "outVars", "{}")
                        self.cf.writeSection(case_id, "chkVars", "{}")
                        self.cf.writeSection(case_id, "afterCase", "[]")
                        self.cf.writeSection(case_id, "runNum", "1")
                        #self.cf.writeSection(case_id, "param_def", '["%s"]' %info["path"])
                        self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                        self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])

    def delCaseDep(self, **info):
        section = list(info.keys())[0]
        self.cf.removeSection(section)
        return "Delete %s Succuss "%section

    def delCaseResult(self, **info):
        section = list(info.keys())[0]
        self.rf.removeSection(section)
        return "Delete %s Succuss "%section

    def getCaseResult(self, **info):
        if DEBUG:
            print(info)
        if len(info) != 0:
            section = list(info.keys())[0]
            ret = self.getCaseDetail(section)
            return [ret]
        sections = self.rf.getAllSection()
        infoList = []
        for section in sections:
            if section == "common":
                continue
            ret = self.getCaseDetail(section)
            if ret is False:
                continue
            infoList.append(ret)
        return infoList

    def getDictResult(self, strInfo):
        retDict = {}
        strList = strInfo.split("|")
        if len(strList) < 7:
            print(strInfo)
        try:
            retDict["APIFunction"] = strList[0]
            retDict["http_method"] = strList[1]
            retDict["path"] = strList[2]
            retDict["url"] = strList[3]
            retDict["body"] = strList[4]
            retDict["TestTime"] = strList[5]
            retDict["TestResult"] = strList[6]
            if len(strList) >= 8:
                retDict["FailReason"] = strList[7]
            else:
                retDict["FailReason"] = ""
            if len(strList) >= 9:
                retDict["Response"] = strList[8]
            else:
                retDict["Response"] = ""
        except Exception as e:
            print("getDictResult exception: ", e)
            print("strInfo", strInfo)
            print("retDict", retDict)
        retDict["case_id"] = "%s_%s"%(retDict["http_method"], retDict["path"])
        return retDict

    def getCaseLoopResult(self, **info):
        infoList = []
        resultList = getApiStringList(self.project, mode="result")
        if len(info) != 0:
            section = list(info.keys())[0]
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                if section == retDict["case_id"]:
                    infoList.append(retDict)
        else:
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                infoList.append(retDict)
        return infoList

    def getTestReport(self, **info):
        resultList = getApiStringList(self.project, mode="result")
        if len(info) != 0:
            dictInfo = {}
            count = 0
            fCount = 0
            sCount = 0
            uCount = 0
            section = info.keys()[0]
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                if section == retDict["case_id"]:
                    dictInfo["APIFunction"] = retDict["APIFunction"] 
                    count = count + 1
                    if retDict["TestResult"] == "failure":
                        fCount = fCount + 1
                    elif retDict["TestResult"] == "success":
                        sCount = sCount + 1
                    else:
                        uCount = uCount + 1
                    dictInfo["TestResult"] = retDict["TestResult"]
                    dictInfo["FailReason"] = retDict["FailReason"]
            dictInfo["testTimes"] = count
            dictInfo["passTimes"] = sCount
            dictInfo["failTimes"] = fCount
            dictInfo["untestTimes"] = uCount
            dictInfo["case_id"] = section
            return [dictInfo]
        else:
            sections = self.cf.getAllSection()
            #sourceList = getApiStringList(self.project, mode="source")
            infoList = []
            for section in sections:
                if section == "common":
                    continue
                rawString = self.cf.getOption(section, "raw")
                if rawString:
                    apiInfo = rawString.replace("\"", "").split("|")
                else:
                    print("section: ", section)
                    print("rawString: ", rawString)
                    return infoList
            # for strSource in sourceList:
            #     apiInfo = strSource.split("|")
                dictInfo = {}
                section = "%s_%s"%(apiInfo[2], apiInfo[3])
                count = 0
                fCount = 0
                sCount = 0
                uCount = 0
                self.cf.getOption(section, "runNum")
                dictInfo["APIFunction"] = apiInfo[0]
                dictInfo["runTimes"] = self.cf.getOption(section, "runNum") 
                for resultStr in resultList:
                    if DEBUG:
                        print(resultStr)
                    retDict = self.getDictResult(resultStr)
                    if section == retDict["case_id"]:
                        count = count + 1
                        if retDict["TestResult"] == "untested":
                            uCount = uCount + 1
                        elif retDict["TestResult"] == "success":
                            sCount = sCount + 1
                        else:
                           fCount = fCount + 1
                        dictInfo["FailReason"] = retDict["FailReason"]
                if sCount > 0:
                    dictInfo["TestResult"] = "success"
                elif fCount > 0:
                    dictInfo["TestResult"] = "failure"
                elif uCount > 0:
                    dictInfo["TestResult"] = "untested"
                if count == 0:
                    dictInfo["TestResult"] = ""
                    dictInfo["FailReason"] = ""
                dictInfo["testTimes"] = count
                dictInfo["passTimes"] = sCount
                dictInfo["failTimes"] = fCount
                dictInfo["untestTimes"] = uCount
                dictInfo["case_id"] = section
                infoList.append(dictInfo)
            return infoList

    def getCountData(self, *infoList):
        sourceList = getApiStringList(self.project, mode="source")
        allCount = len(sourceList)
        sections = self.cf.getAllSection()
        unautomatableCount = 0
        for section in sections:
            runNum = self.cf.getOption(section, "runNum")
            if runNum and int(runNum) == 0:
                unautomatableCount = unautomatableCount + 1
        passCount = 0
        failCount = 0
        unTestCount = 0
        for info in infoList:
            if info["TestResult"] == "failure":
                failCount = failCount + 1
            elif info["TestResult"] == "success":
                passCount = passCount + 1
            elif info["TestResult"] == "untested":
                pass
            else:
                unTestCount = unTestCount + 1
        countDict = {}
        countDict["allCount"] = allCount
        countDict["automatableCount"] = allCount - unautomatableCount
        countDict["unautomatableCount"] = unautomatableCount
        countDict["autoTestCount"] = passCount + failCount
        countDict["unTestCount"] = unTestCount
        countDict["passCount"] = passCount
        countDict["failCount"] = failCount
        if countDict["allCount"] == 0:
            countDict["autoPer"] = 0
        else:
            countDict["autoPer"] = '{:.2%}'.format(round(countDict["automatableCount"], 2) / round(countDict["allCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["passPer"] = 0
        else:
            countDict["passPer"] = '{:.2%}'.format(round(countDict["passCount"], 2) / round(countDict["autoTestCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["failPer"] = 0
        else:
            countDict["failPer"] = '{:.2%}'.format(round(countDict["failCount"], 2) / round(countDict["autoTestCount"], 2))

        return countDict

class HostEnv(object):
    """docstring for HostEnv"""
    def __init__(self):
       self.hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))

    def postHostEnv_27(self, **info):
        section = info["PRODUCTION"][0]
        if len(section) == 0:
            return 
        for option in info.keys():
            if option == "modify":
                continue
            value = info[option][0]
            self.hf.writeSection(section, option, value)
        return "Add %s Success "%section

    def postHostEnv(self, **info):
        section = info["PRODUCTION"]
        if len(section) == 0:
            return 
        for option in info.keys():
            if option == "modify":
                continue
            value = info[option]
            self.hf.writeSection(section, option, value)
        return "Add %s Success "%section


    def deleteHostEnv(self, **info):
        section = list(info.keys())[0]
        self.hf.removeSection(section)
        return "Delete %s Succuss "%section

    def putHostEnv(self, **info):
        section = info["production"]
        for option in info.keys():
            value = info[option]
            self.hf.writeSection(section, option, value)
        return "Modify %s Success "%section

    def getEnvHost(self):
        infoList = []
        sections = self.hf.getAllSection()
        for section in sections:
            options = self.hf.getAllItem(section)
            options["PRODUCTION"] = section
            infoList.append(options)
        return infoList

class Env(object):
    """docstring for Env"""
    def __init__(self, project):
        #rConfig = "%s-API-Result.ini"%project.upper()
        rConfig = "%s-API-Dependancy.ini"%project.upper()
        self.rf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, rConfig))
        commonOption = ["noChkVar", "uniVar"]
        for option in commonOption:
            if not self.rf.getOption("common", option):
                self.rf.writeSection("common",  option, "[]")

    def postEnv(self, var_id, value):
        ret = self.rf.getOption("common", var_id)
        self.rf.writeSection("common", var_id, value)
        return "Save %s Env Var Succuss ~ "%(var_id)

    def getEnv(self, **info):
        if not self.rf.getSection("common"):
            return []
        if len(info) != 0:
            option = info.keys()[0]
            value = self.rf.getOption("common", option)
            if value is False:
                return [{"name": option, "value": "Not Define"}]
            else:
                return [{"name": option, "value": value}]
        options = self.rf.getAllOption("common")
        infoList = []
        for option in options:
            value = self.rf.getOption("common", option)
            if value is False:
                continue
            infoList.append({"name": option, "value": value})
        return infoList

    def deleteEnv(self, **info):
        option = list(info.keys())[0]
        self.rf.removeOption("common", option)
        return "Delete %s Succuss "%option

class Source(object):
    def __init__(self, project):
        self.project = project
        dConfig = "%s-API-Dependancy.ini"%project.upper()
        self.df = localConfigParser("%s/local/%s/%s"%(curPath, configPath, dConfig))

    def getSConfig(self):
        infoList = []
        sections = self.df.getAllSection()
        for section in sections:
            if section == "common":
                continue
            apiString = self.df.getOption(section, "raw")
            if not apiString:
                continue
            apiString = apiString.replace("\"", "")
            apiDict = {}
            # if DEBUG:
            #     print("apiString: ", apiString)
            if len(apiString) == 0:
                continue
            apiList = apiString.split("|")
            if DEBUG:
                apiList
            try:
                apiDict["APIFunction"] = apiList[0]
                apiDict["protocol"] = apiList[1]
                apiDict["http_method"] = apiList[2]
                apiDict["path"] = apiList[3]
                if len(apiList[5]) != 0:
                    apiDict["pathVariable"] = eval(apiList[5])
                else:
                    apiDict["pathVariable"] = apiList[5]
                if len(apiList[6]) != 0:
                    apiDict["queryParameter"] = eval(apiList[6])
                else:
                    apiDict["queryParameter"] = apiList[6]
                if len(apiList[7]) != 0:
                    apiDict["body"] = eval(apiList[7])
                else:
                    apiDict["body"] = apiList[7]
                if len(apiList[8]) != 0:
                    apiDict["response"] = eval(apiList[8])
                else:
                    apiDict["response"] = apiList[8]
                apiDict["case_id"] = "%s_%s"%(apiDict["http_method"], apiDict["path"])
                apiDict["raw"] = apiString
                infoList.append(apiDict)
            except Exception as e:
                print("getSConfig exception: ", e)
                print("apiString: ", apiString)
        return infoList

    def postSConfig(self, **info):
        if len(info['http_method'])==0 or len(info['path'])==0:
            return "Please Input http_method and path"
        String = '\"%s|%s|%s|%s|%s|%s|%s|%s|%s\"'%(info['APIFunction'], info['protocol'], info['http_method'], info['path'], str(info['header']).replace('\"', '\''), str(info['pathVar']).replace('\"', '\''), str(info['queryParam']).replace('\"', '\''), str(info['body']).replace('\"', '\''), str(info['response']).replace('\"', '\''))
        section = "%s_%s" %(info['http_method'], info['path'])
        self.df.writeSection(section,"raw", String)
        return True

    def delSConfig(self, **info):
        section = list(info.keys())[0]
        self.df.removeSection(section)
        return True
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(version='1.1', description="Create API Info File for Auto Test")
    parser.add_argument('-m','--module', dest="module", action="store", default="N", help="%s; default value is N for Not, [ all ] for all modules"%modules.keys())
    parser.add_argument('-r','--run', dest="runAPI", action="store", default="None", help="[ Y/N ] Y for Yes, N for No;default value is [ None ] for Empty")
    parser.add_argument('-t','--api', dest="targetAPI", action="store", default="None", help="[ method_API/all ], [ get_/device/{sn}/app-user ] for special api , [ all ] for all API, default value is [ None ] for Empty")
    parser.add_argument('-H','--human-readable', dest="manRead", action="store", default="Y", help="[ Y/N ] Y for Yes, N for No;default value is [ Y ]")
    parser.add_argument('-n','--number', dest="number", action="store", default=1, help="[ 0/1/xxx ] 1 for all times, xxx for xxx times;default value is [ 1 ]")
    args = parser.parse_args()
    runModes = ["Y", "N"]
    if args.runAPI.upper == "N":
        parser.print_help()
    elif (args.runAPI.upper() == "Y") and (args.targetAPI.upper() == "ALL"):
        runAPIs(args.module.upper())
    elif args.targetAPI == "None":
        parser.print_help()
    else:
        status, output = runTargetAPI(args.module.upper(), args.targetAPI, args.number, mode="loop")
        if not status:
            print(output)
