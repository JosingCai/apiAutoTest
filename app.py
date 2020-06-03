#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import local.apicase as apicase
import local.testcase as testcase
import local.swagger as swagger
import local.report as report
#import local.envChk as envChk
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__,static_url_path='',root_path='')
IP = "127.0.0.1"
PORT = "8888"

jinja_environ = app.create_jinja_environment()
jinja_environ.globals['LINK_PATH_HEAD'] = "%s:%s" %(IP, PORT)

api = Api(app)

#get 其他年轻是通过flask.request.args来获取
#post请求是通过flask.request.form来获取
# CSRF是跨站请求伪造的随机字符串

@app.route('/form', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        username = request.form.get("usename")
        password = request.form.get("password")
        password2 = request.form.get("password2")
    if login_form.validate_on_submit():
        return "success"
    else:
        flash("参数有误")
    return render_template('test.html', form=login_form)

@app.route("/report")
def reportAll():
    handle = report.Report()
    infoList = handle.get_table_list(**request.args)
    return render_template("reportAll.html", transList=infoList)

@app.route("/report/detail")
def reportTableInfo():
    handle = report.Report()
    table_info = {}
    table_info["cn_name"] = request.args["cn_name"].encode("utf-8")
    table_info["en_name"] = request.args["en_name"].encode("utf-8")
    infoList = handle.get_table_info(**request.args)
    return render_template("reportTable.html", transList=infoList,table_info=table_info)

@app.route("/report/sql", methods=["GET", "POST"])
def reportSQL():
    handle = report.Report()
    if request.method == "POST":
        parameters = request.form 
        handle.post_sql(**parameters)
    infoList = handle.get_sql_info()
    return render_template("reportSQL.html", transList=infoList)

@app.route("/<project>/case")
def caseAll(project):
    project = project.upper()
    handle = apicase.Case(project)
    caseList = handle.getCase(**request.args)
    return render_template("caseAll.html", project=project, transList=caseList)

@app.route("/<project>/case/dep/sync",methods=["POST"])
def syncCaseDep(project):
    project = project.upper()
    handle = apicase.Case(project)
    if request.method == "POST":
        handle.syncCaseDep()
    caseList = handle.getCaseDep(**request.args)
    return render_template("caseAll.html", project=project, transList=caseList)

@app.route("/<project>/case/dep",methods=["GET", "POST"])
def caseDep(project):
    project = project.upper()
    handle = apicase.Case(project)
    if request.method == "POST":
        handle.postCaseDep(**request.form)
    caseList = handle.getCaseDep(**request.args)
    return render_template("caseDep.html", project=project, transList=caseList)

@app.route("/<project>/case/dep/remove", methods=["POST"])
def caseDepRemove(project):
    project = project.upper()
    handle = apicase.Case(project)
    handle.delCaseDep(**request.form)
    caseList = handle.getCaseDep()
    return render_template("caseDep.html", project=project, transList=caseList)

@app.route("/<project>/case/result")
def caseResult(project):
    project = project.upper()
    handle = apicase.Case(project)
    caseList = handle.getCaseResult(**request.args)
    return render_template("caseResult.html", project=project, transList=caseList)

@app.route("/<project>/case/result/remove", methods=["POST"])
def caseResultRemove(project):
    project = project.upper()
    handle = apicase.Case(project)
    handle.delCaseResult(**request.form)
    caseList = handle.getCaseResult()
    return render_template("caseResult.html", project=project, transList=caseList)

@app.route("/<project>/case/result/detail")
def caseResultDetail(project):
    project = project.upper()
    handle = apicase.Case(project)
    caseList = handle.getCaseLoopResult(**request.args)
    return render_template("caseResultDetail.html", project=project, transList=caseList)

@app.route("/<project>/report")
def testReport(project):
    project = project.upper()
    handle = apicase.Case(project)
    caseList = handle.getTestReport(**request.args)
    countDict = handle.getCountData(*caseList)
    return render_template("testReport.html", project=project, transList=caseList, infoDict=countDict)

@app.route("/<project>/comVar", methods=['GET', 'POST'])
def comVar(project):
    project = project.upper()
    handle = apicase.Env(project)
    if request.method == "POST":
        handle.postEnv(request.form["name"], request.form["value"])
    envList = handle.getEnv(**request.args)
    return render_template("comVar.html", project=project, transList=envList)

@app.route("/<project>/comVar/remove", methods=["POST"])
def comVarRemove(project):
    project = project.upper()
    handle = apicase.Env(project)
    handle.deleteEnv(**request.form)
    envList = handle.getEnv()
    return render_template("comVar.html", project=project, transList=envList)

@app.route("/<project>/envConfig", methods=['GET', 'POST'])
def envConfig(project):
    project = project.upper()
    handle = envChk.envConfig(project)
    if request.method == "POST":
        handle.postEnvConfig(request.form["name"], request.form["value"])
    envConfigList = handle.getEnvConfig(**request.args)
    return render_template("envConfig.html", project=project, transList=envConfigList)
 
@app.route("/<project>/envConfig/all", methods=['GET', 'POST'])
def envAllConfig(project):
    project = project.upper()
    handle = envChk.envConfig(project)
    envConfigList = handle.envConfigAll()
    return render_template("envConfig.html", project=project, transList=envConfigList)

@app.route("/<project>/case/run", methods=['POST'])
def runCase(project):
    project = project.upper()
    handle = apicase.RunCase(project)
    infoList = handle.run(**request.form)
    return render_template("caseRun.html", project=project, transList=infoList)

@app.route("/<project>/case/run/all", methods=['POST'])
def runAllCase(project):
    handle = apicase.RunCase(project)
    infoList = handle.runAll()
    return render_template("caseRun.html", project=project, transList=infoList)

@app.route("/<project>/source",methods=["GET", "POST"])
def getSource(project):
    project = project.upper()
    handle = apicase.Source(project)
    if request.method == "POST":
        handle.postSConfig(**request.form)
    retList = handle.getSConfig()
    return render_template("source.html", project=project, transList=retList)

@app.route("/<project>/source/auto",methods=["POST"])
def getSourceAuto(project):
    project = project.upper()
    handle = swagger.AutoSource(project)
    if request.method == "POST":
        chenges = handle.createAutoData()
        return render_template("source_change.html", project=project, transList=chenges)
    handle = apicase.Source(project)
    retList = handle.getSConfig()
    return render_template("source.html", project=project, transList=retList)

@app.route("/<project>/source/remove",methods=["POST"])
def deleteSource(project):
    project = project.upper()
    handle = apicase.Source(project)
    handle.delSConfig(**request.form)
    retList = handle.getSConfig()
    return render_template("source.html", project=project, transList=retList)

# @app.route("/<project>/source/put",methods=["POST"])
# def modifySource(project):
#     project = project.upper()
#     handle = apicase.Source(project)
#     handle.putSConfig(**request.form)
#     retList = handle.getSConfig()
#     return render_template("source.html", project=project, transList=retList)

@app.route("/<project>/testcase/<int:sheet_index>",methods=["GET", "POST"])
def get_test_case(project, sheet_index):
    project = project.upper()
    handle = testcase.TestCase(project)
    index_list = handle.get_sheet_names()
    count = 0
    for info in index_list:
        if sheet_index == info["index"]:
            sheet_name = info['name']
            break
        else:
            count = count + 1
        if count == len(index_list):
            sheet_name = '新需求'
    if request.method == "POST":
        retList = handle.add_case(sheet_name, **request.form)
    else:
        retList = handle.get_sheet_content(sheet_name)

    return render_template("test_case.html", project=project, transList=retList[1:], sheets_list=index_list, titles=retList[0], sheet_index=sheet_index)

@app.route("/<project>/testcase/<int:sheet_index>/put",methods=["POST"])
def put_test_case(project, sheet_index):
    project = project.upper()
    handle = testcase.TestCase(project)
    index_list = handle.get_sheet_names()
    count = 0
    for info in index_list:
        if sheet_index == info["index"]:
            sheet_name = info['name']
            break
        else:
            count = count + 1
        if count == len(index_list):
            sheet_name = '新需求'
    status, output = handle.modify_case(sheet_name, **request.form)
    return redirect(url_for("get_test_case", project=project, sheet_index=sheet_index))

@app.route("/<project>/testcase/<int:sheet_index>/test",methods=["POST"])
def run_test_case(project, sheet_index):
    project = project.upper()
    handle = testcase.TestCase(project)
    index_list = handle.get_sheet_names()
    count = 0
    for info in index_list:
        if sheet_index == info["index"]:
            sheet_name = info['name']
            break
        else:
            count = count + 1
        if count == len(index_list):
            sheet_name = '新需求'
    status, infoList = handle.run_case(sheet_name, **request.form)
    return render_template("caseRun.html", project=project, transList=infoList)

@app.route("/<project>/testcase/<int:sheet_index>/delete",methods=["POST"])
def delete_test_case(project, sheet_index):
    project = project.upper()
    handle = testcase.TestCase(project)
    index_list = handle.get_sheet_names()
    for info in index_list:
        if sheet_index == info["index"]:
            sheet_name = info['name']
            status, output = handle.delete_case(info['name'],**request.form)
            break
    return redirect(url_for("get_test_case", project=project, sheet_index=sheet_index))

@app.route("/<project>/testcase/split",methods=["POST"])
def split_test_case(project):
    project = project.upper()
    handle = testcase.TestCase(project)
    status, output = handle.split_case(r"新需求")
    return redirect(url_for("get_test_case", project=project, sheet_index=0))

@app.route("/test/host",methods=["GET", "POST"])
def getTestHost():
    handle = apicase.HostEnv()
    if request.method == "POST":
        handle.postHostEnv(**request.form)
    retList = handle.getEnvHost()
    return render_template("testHost.html", transList=retList)

@app.route("/test/host/remove",methods=["POST"])
def deleteTestHost():
    handle = apicase.HostEnv()
    handle.deleteHostEnv(**request.form)
    retList = handle.getEnvHost()
    return render_template("testHost.html", transList=retList)

@app.route("/test/host/modify",methods=["POST"])
def modifyTestHost():
    handle = apicase.HostEnv()
    handle.putHostEnv(**request.form)
    retList = handle.getEnvHost()
    return render_template("testHost.html", transList=retList)

@app.route("/")
def envIndex():
    handle = apicase.HostEnv()
    retList = handle.getEnvHost()
    return render_template("testHost.html", transList=retList)

if __name__ == '__main__':
    app.run(host=IP, port=PORT, debug=True)