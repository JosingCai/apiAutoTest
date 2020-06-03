#!/usr/bin/env python
# -*- coding: utf-8 -*-

from local.function.comModVar import *
from local.function.base import *
from local.report import Database

code_path_base = "%s/tools/path" %curPath

def update_swagger(module, branch):
    cmd0 = "cd %s/path" %code_path_base
    cmd1 = "pwd"
    cmd2 = "git checkout %s && git pull" %branch
    cmd3 = "swagger generate spec -o %s/doc/api/swagger.json" %code_path_base
    cmd4 = "cp -f %s/doc/api/swagger.json %s/%s/%s.json" %(code_path_base, curPath, sourceFPath, module)
    cmd5 = "cd -"
    cmds = [cmd0, cmd1, cmd2, cmd3, cmd4, cmd5]
    for cmd in cmds:
        status, output = commands.getstatusoutput(cmd)
        print("cmd: ", cmd)
        print("output: ", output)
        if status != 0:
            return False, "Get %s Swagger File Failed, Please Check it ~" %module
    return True

def analysis(module):
    cmd = "ls %s/local/%s/%s*" %(curPath,sourceFPath, module)
    status, output = commands.getstatusoutput(cmd)
    if status != 0:
        print("output: ", output)
        return False, "Get %s Swagger File Failed, Please Check it ~" %module
    fileList = output.split("\n")
    fileName = fileList[0]
    with open(fileName) as f:
        content = f.read()
    if fileName.endswith(".yaml"):
        rawDict = yaml.load(content)
    elif fileName.endswith(".json"):
        rawDict = json.loads(content)
    else:
        print("Not Support Current %s Format File" %fileName)
    definitions = rawDict["definitions"]
    simple_def_dict = {}
    full_def_dict = {}
    response_dict = {}
    mult_def_key = []
    informal_def = []

    def_desc_all = {}
    for Key in definitions.keys():
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            def_desc = {}
            for subKey in properties.keys():
                if "description" in properties[subKey]:
                    def_desc[subKey] = properties[subKey]["description"]
                else:
                    def_desc[subKey] = ""
        def_desc_all[Key] = def_desc

    for Key in definitions.keys(): 
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            subDict = {}
            for subKey in properties.keys():
                if "$ref" in properties[subKey]:
                    def_dict = {}
                    obj = properties[subKey]["$ref"].split("/")[-1]
                    def_dict["name"] = subKey
                    def_dict["value"] = obj
                    mult_def_key.append(def_dict)
                    break
                subDict[subKey] = properties[subKey]["type"]
            simple_def_dict[Key] = subDict
        else:
            informal_def.append(Key)
            simple_def_dict[Key] = ""
    for Key in definitions.keys(): 
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            subDict = {}
            for subKey in properties.keys():
                if "$ref" in properties[subKey]:
                    obj = properties[subKey]["$ref"].split("/")[-1]
                    subDict[subKey] = simple_def_dict[obj]
                else:
                    subDict[subKey] = properties[subKey]["type"]
            Key = Key.encode("utf-8").decode("utf-8")
            full_def_dict[Key] = subDict
    if "responses" in rawDict:
        response_info = rawDict["responses"]
    else:
        response_info = {}
    for Key in response_info.keys():
        if "schema" in response_info[Key]:
            try:
                properties = response_info[Key]["schema"]["properties"]["content"]["properties"]
                sub_dict = {}
                for subKey in properties.keys():
                    sub_dict[subKey] = properties[subKey]["type"] 
                response_dict[Key] = sub_dict
            except Exception as e:
                print("resp exception: ", e)
                print("resp: ", response_info[Key])
        else:
            print("resp: ", response_info[Key])
            print("undef key: ", subKey)
            response_dict[Key] = ""
    simple_def_dict.update(response_dict)
    simple_def_dict.update(full_def_dict)
    items = rawDict["paths"]
    infoList = []
    for item in items.keys():
        path = item.encode("utf-8").decode("utf-8")
        apiCollection = items[item]
        for method in apiCollection.keys():
            infoDict = {}
            infoDict["varDesc"] = {}
            apiInfo = apiCollection[method]
            if "tags" in apiInfo:
                infoDict["group"] = apiInfo["tags"][0]
            else:
                infoDict["group"] = "Other"
            infoDict['http_method'] = method.encode("utf-8").decode("utf-8")
            infoDict['APIFunction'] = apiInfo["summary"].encode("utf-8").decode("utf-8")
            try:
                infoDict['response'] = apiInfo["responses"]
            except Exception as e:
                print("1 exception: ", e)
                infoDict['response'] = ""
            infoDict['path'] = path
            try:
                responseList = apiInfo["responses"]["200"]["$ref"].split("/")
                responseKey = responseList[-1]
            except Exception as e:
                print("2 exception: ", e)
                responseKey = ""
            try:
                infoDict['response'] = simple_def_dict[responseKey]
            except Exception as e:
                print("3 exception: ", e)
                infoDict['response'] = ""
            try:
                parameters = apiInfo["parameters"]
            except Exception as e:
                print("4 exception: ", e)
                parameters = ""

            parameList = []
            headerDict = {}
            queryDict = {}
            bodyDict = {}
            pathDict = {}
            descDict = {}

            for i in range(len(parameters)):
                parameDict = {}
                parameter = parameters[i]
                if parameter["in"] == "body":
                    if "$ref" in parameter['schema']:
                        subparameList = parameter['schema']["$ref"].split("/")
                        defiKey = subparameList[-1]
                        if defiKey =="PostDeviceReq":
                            parameDict["parameValue"] = simple_def_dict['Device']
                        else:
                            parameDict["parameValue"] = simple_def_dict[defiKey]
                        infoDict["varDesc"].update(def_desc_all[defiKey])
                    else:
                        parameDict["parameValue"] = parameter['schema']["type"]
                elif parameter["in"] == "query":
                    if "$ref" in parameters[i]:
                        obj = parameters[i]["$ref"].split("/")[-1]
                        parameDict["parameValue"] = simple_def_dict[obj]
                        infoDict["varDesc"].update(def_desc_all[obj])
                    else:
                        try:
                            parameDict["parameValue"] = parameter["type"]
                        except Exception as e:
                            print("5 exception: ", e)
                            parameDict["parameValue"] = ""
                else:
                    try:
                        parameDict["parameValue"] = parameter["type"]
                    except Exception as e:
                        print("type exception: ", e)
                        parameDict["parameValue"] = ""

                parameDict["parameName"] = parameter["name"]
                try:
                    parameDict["parameDesc"] = parameter["description"]
                except Exception as e:
                    print("description exception: ", e)
                    parameDict["parameDesc"] = ""
                parameDict["parameType"] = parameter["in"]
                parameList.append(parameDict)

            for info in parameList:
                if len(info) == 0:
                    continue
                if info["parameType"] == "header":
                    headerDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "query":
                    queryDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "body":
                    bodyDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "path":
                    pathDict[info["parameName"]] = info["parameValue"]
                descDict[info["parameName"]] = info["parameDesc"]
            infoDict["header"] = headerDict
            if "Body" in queryDict:
                infoDict["queryParameter"] = queryDict["Body"]
            else:
                infoDict["queryParameter"] = queryDict
            infoDict["body"] = bodyDict
            infoDict["pathVariable"] = pathDict
            infoDict["varDesc"].update(descDict)
            infoList.append(infoDict)
    return infoList

def createCustomF(module, manRead):
    curTime=datetime.datetime.now().strftime('%Y%m%d') 
    if manRead == "Y":
        targetFN = "%s/local/%s/H-%s-API-Custom-%s.csv"%(curPath, CSVPath,module, curTime)
    else:
        targetFN = "%s/local/%s/%s-API-Custom.csv"%(curPath, CSVPath,module)
        bakFN = "%s/local/%s/bak/%s-API-Custom-%s.csv"%(curPath, CSVPath,module, curTime)
        if os.path.exists(targetFN):
            cmd = "mv %s %s" %(targetFN, bakFN)
            status, output = commands.getstatusoutput(cmd)
            if status != 0:
                print("cmd: ", cmd)
                print("output: ", output)
        else:
            open(targetFN, "w").close()
    infoList = analysis(module)
    with open(targetFN, 'a+') as f:
        #tableHeader = "group|APIFunction|protocol|http_method|path|header|pathVariable|queryParameter|body|response"
        tableHeader = "APIFunction|protocol|http_method|path|header|pathVariable|queryParameter|body|response"
        f.write("%s\n"%tableHeader)
        change_list = []
        for info in infoList:
            http_method = info["http_method"]
            path = info["path"]
            APIFunction = info["APIFunction"]
            group = info["group"]
            try:
                if len(info["response"]) == 0:
                    response = ""
                else:
                    response = str(info["response"]) 
            except Exception as e:
                print("exception: ", e)
                response = ""
            try:
                if len(info["header"]) == 0:
                    header = ""
                else:
                    header = str(info["header"])
            except Exception as e:
                print("exception: ", e) 
                header = ""
            try:
                if len(info["pathVariable"]) == 0:
                    pathVariable = ""
                else:
                    # print(info["pathVariable"])
                    pathVariable = str(info["pathVariable"])
                    # print("pathVariable: ", pathVariable)
            except Exception as e:
                print("exception: ", e) 
                pathVariable = ""
            try:
                if len(info["queryParameter"]) == 0:
                    queryParameter = ""
                else:
                    queryParameter = str(info["queryParameter"])
                    
            except Exception as e:
                print("exception: ", e)
                pathVariable = ""
            try:
                com_key = "Body"
                if com_key in info['body']:
                    if len(info["body"][com_key]) == 0:
                        body = ""
                    else:
                        body = str(info["body"][com_key])
                elif com_key in info['body']:
                    if len(info["body"][com_key]) == 0:
                        body = ""
                    else:
                        body = str(info["body"][com_key])
                elif "data" in info["body"]:
                    body = str(info["body"]['data'])
                else:
                    body = ""
            except Exception as e:
                print("exception: ", e)
                body = ""
            #String = group + "|" + APIFunction + "|" + PROTOCOL + "|" + http_method + "|" + path + "|" + header + "|" + pathVariable + "|" +queryParameter + "|" + body + "|" + response
            String = APIFunction + "|" + PROTOCOL + "|" + http_method + "|" + path+ "|" + header + "|" + pathVariable + "|" + queryParameter + "|" + body + "|" + response
            f.write("%s\n"%String)
            c_file = "%s-API-Dependancy.ini"%module
            c_handle = localConfigParser("local/%s/%s"%(configPath, c_file))
            section = "%s_%s" %(info["http_method"], info["path"])
            if not c_handle.hasSection(section):
                c_handle.writeSection(section, "raw", '"%s"' %String)
            else:
                #c_handle.writeSection(section, "raw", '"%s"' %String)
                old_string = c_handle.getOption(section, "raw")
                if '"%s"' %String != old_string:
                    change_dict = {}
                    change_dict["section"] = section
                    change_dict["old_raw"] = old_string
                    change_dict["new_raw"] = '"%s"' %String
                    change_list.append(change_dict)
            
            def_list = []
            for item in info["varDesc"]:
                if "字典编码" in info["varDesc"][item]:
                    results = re.findall('[a-zA-Z0-9_]+', info["varDesc"][item])
                    if len(results) > 0:
                        type_name = results[0]
                        def_list.append(type_name)
            status, output = get_db_config(module)
            if status:
                dbhandler = Database(output)
                for item in def_list:
                    value_list = dbhandler.get_sys_var_info(item)
                    value_dict = c_handle.getOption("common", section)
                    name = item.split("_")[-1]
                    if value_dict:
                        value_dict = eval(value_dict)
                        value_dict.update({name:value_list})
                        c_handle.writeSection("common", section, str(value_dict))
                    else:
                        value_dict = {name:value_list}
                        c_handle.writeSection("common", section, str(value_dict))
                dbhandler.close_handler()
            else:
                print("Link DB Failed, %s" %output)
            
        return change_list

    if manRead == "Y":
        humanReadable(targetFN)
        return True

class AutoSource(object):
    """docstring for Source"""
    def __init__(self, project):
        self.project = project
        #self.hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))

    def createAutoData(self):
        # branch = self.hf.getOption(self.project, "branch")
        # if not branch:
        #     return True, "Please Appoint branch info"
        # ret = update_swagger(self.project, branch)
        # if not ret[0]:
        #     return ret[1]
        changes = createCustomF(self.project, manRead="N")
        return changes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(version='1.1', description="Create API Info File for Auto Test")
    parser.add_argument('-m','--module', dest="module", action="store", default="N", help="Project Name; default value is N for Not")
    parser.add_argument('-H','--human-readable', dest="manRead", action="store", default="Y", help="[ Y/N ] Y for Yes, N for No;default value is [ Y ]")
    args = parser.parse_args()

    if args.module.upper() == "N":
        parser.print_help()
    else:
        createCustomF(args.module.upper(), args.manRead)
    
