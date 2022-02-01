#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from typing import no_type_check
import sys
import requests
import json
import re
import copy
import subprocess
from requests.api import get
import urllib3
urllib3.disable_warnings()
sys.path.insert(0, '/data/usnmp/Scripts_all_day/step/convert_metrics')
import dashbord

jsonchick_osn = {
    "dash_title"  : [],
    "datasourse"  : [],
    "highMetric"  : [],
    "lowMetrics"  : []
}

lowMetric = {
    "name"    : [],
    "batches" : []
}

batche = {
    "select"         : [],
    "crit_duration"  : [],
    "error_duration" : [],
    "crit_sign"      : [],
    "error_sign"     : [],
    "crit_limit"     : [],
    "error_limit"    : [],
    "crit_severity"  : [],
    "error_severity" : [],
    "crit_minstep"   : [],
    "error_minstep"  : [],
    "groupBy"        : [],
    "influxBank"     : []
}



def batch_json(tick):
    jsonchick = copy.deepcopy(jsonchick_osn)
    basetick = tick['base']
    fmtick = tick['fm']
    db = ""
    base_data = open('/data/usnmp/Scripts_all_day/KAPACITOR/' + basetick, 'r').read()
    fm_data = open('/data/usnmp/Scripts_all_day/KAPACITOR/' + fmtick, 'r').read()
    datasourse = ""
    for var in base_data.split('\n'):
        claster = ' '.join(re.findall(r".*var cluster = '(\D+).*'.*", var))
        get_db = ' '.join(re.findall(r".*var db = '(\D+).*'.*", var))
        if get_db != '':
            db = get_db
        if claster != '':
            if claster == "telegraf":
                datasourse = "Prometheus (prod)"
            else:
                datasourse = "Prometheus (others)"

    product = ' '.join(re.findall(r"var product = '(base\w+)'", base_data))
    high_metric = product.replace('base','fm')
    dash_title = fmtick.replace('.tick', '')
    jsonchick['dash_title'] = dash_title
    jsonchick['datasourse'] = datasourse
    jsonchick['highMetric'] = high_metric
    for level in base_data.split('//fm'):
        low_metric = 'fm' + level.split('\n')[0]
        lowMetrics = copy.deepcopy(lowMetric)
        lowMetrics['name'] = low_metric
        for batch in level.split('batch'):
            batches = copy.deepcopy(batche)
            groupBy = ""
            crit_duration = ""
            error_duration = ""
            crit_repeat_uslovie = ""
            error_repeat_uslovie = ""
            unit = ""
            perem_repeat_uslovie = ""
            perem_unit = ""
            select = ""
            crit_sign = ""
            error_sign = ""
            crit_limit = ""
            error_limit = ""
            crit_unit = ""
            error_unit = ""
            stateDuration = False
            if batch.find('|query') != -1:
                groupBy_time = ""
                select  = ' '.join(re.findall(r"""'''([^<>]+)'''""", batch))
                print(select)
                groupBy = ' '.join(re.findall(r'groupBy\((\S+)\)', batch))
                if re.search(r'.*time\((\d+[smhw])\).*',groupBy):
                    groupBy_time = re.sub(r".*time\((\d+[smhw])\).*",r"\1", groupBy)
                    groupBy = ("(" + re.sub(r"time\(\d+[smhw]\)","", groupBy).replace("'",'') + ")").replace(',)','').replace('(,','')
                if batch.find('stateDuration') != -1: # условие на стате дюратион
                    stateDuration = True
                    for line in batch.split('\n'):
                        repeat_uslovie = re.findall(r"lambda: float\(\"value\"\)([^)]+)", line)
                        perem_unit = ' '.join(re.findall(r".*unit\((\d+[smhw])\).*", line))
                        if len(perem_unit) > 0:
                            unit = str(perem_unit)
                        if len(repeat_uslovie) > 0:
                            perem_repeat_uslovie = repeat_uslovie
                        if line.find("""as('crit_repeat')""") != -1:
                            crit_repeat_uslovie = perem_repeat_uslovie
                            crit_unit = unit
                            for uslovie in crit_repeat_uslovie:
                                crit_sign = re.sub(r"[\d+. ]", "", uslovie)
                                crit_limit = re.sub(r"[!<>= ]","", uslovie).split('.')[0]
                        if line.find("""as('error_repeat')""") != -1:
                            error_repeat_uslovie = perem_repeat_uslovie
                            error_unit = unit
                            for uslovie in error_repeat_uslovie:
                                error_sign  = re.sub(r"[\d+. ]", "", uslovie)
                                error_limit = re.sub(r"[!<>= ]","", uslovie).split('.')[0]

                    error_repeat_times = re.sub(r"[!<>= ]","", (' '.join(re.findall(r"error_repeat\"([^<)]+)", batch))).split(',')[0])
                    if re.search('m', error_unit):
                        error_unit = int(re.sub(r"\D+", r"", error_unit))
                        error_duration = str(int(error_repeat_times * error_unit) + 1) + "m"
                        error_unit = str(error_unit) + "m"
                    elif re.search('s', error_unit):
                        error_unit = int(re.sub(r"\D+", r"", error_unit))
                        error_duration = re.sub(r"\D\d", r"", str(60 / int(error_unit) * int(error_repeat_times) + 1) + "m")
                        error_unit = str(error_unit) + "s"

                    crit_repeat_times  = re.sub(r"[!<>= ]","", (' '.join(re.findall(r"crit_repeat\"([^<)]+)",  batch))).split(',')[0])
                    if re.search('m', crit_unit):
                        crit_unit = int(re.sub(r"\D+", r"", crit_unit))
                        crit_duration = str(int(crit_repeat_times * crit_unit) + 1) + "m"
                        crit_unit = str(crit_unit) + "m"
                    elif re.search('s', crit_unit):
                        crit_unit = int(re.sub(r"\D+", r"", crit_unit))
                        crit_duration = re.sub(r"\D\d", r"", str(60 / int(crit_unit) * int(crit_repeat_times) + 1) + "m")
                        crit_unit = str(crit_unit) + "s"

                else: # доделать
                    stateDuration = False
                    for line in batch.split('\n'):
                        if line.find('//critical') != -1:
                            uslovie = ' '.join(re.findall(r'\) ([^/D)]+)', line))
                            crit_sign = uslovie.split(' ')[0]
                            crit_limit = uslovie.split(',')[0].split(' ')[1].split('.')[0]
                        if line.find('//error') != -1:
                            uslovie = ' '.join(re.findall(r'\) ([^/D)]+)', line))
                            error_sign = uslovie.split(' ')[0]
                            error_limit = uslovie.split(',')[0].split(' ')[1].split('.')[0]
                batches['select']   = select
                if stateDuration == False:
                    batches['crit_duration']  = "1m"
                    batches['error_duration'] = "1m"
                    batches["crit_minstep"] = groupBy_time
                    batches["error_minstep"] = groupBy_time
                else:
                    batches['crit_duration']  = crit_duration
                    batches['error_duration'] = error_duration
                    batches["crit_minstep"]  = crit_unit
                    batches["error_minstep"] = error_unit
                batches["crit_sign"]     = crit_sign
                batches["error_sign"]    = error_sign
                batches["crit_limit"]    = crit_limit
                batches["error_limit"]   = error_limit
                batches["groupBy"]       = groupBy
                batches["influxBank"]    = db
                lowMetrics["batches"].append(batches)
        jsonchick["lowMetrics"].append(lowMetrics)


    for leveler in fm_data.split('var fm'):
        crit_limit = False
        error_severity = ""
        crit_severity = ""
        error_limit = False
        fm_lowMetrics = "fm" + leveler.split('\n')[0].split(' ')[0]
        for lowMetricName in jsonchick["lowMetrics"]:
            if fm_lowMetrics == lowMetricName['name']:
                for line in leveler.split('\n'):
                    # if re.findall(r'eval\(lambda: if\((.*)\)', line) == -1:
                    #     print(line)
                    eval = ' '.join(re.findall(r'eval\(lambda: if\((.*)\)', line)).replace(' ','')
                    if eval != "":
                        if eval.count('crit') > 1 or eval.count('error') > 1:
                            if re.search('2.0', eval):
                                crit_severity = True
                                error_severity = False
                            elif re.search('1.0', eval):
                                crit_severity = False
                                error_severity = True
                        elif eval.count('crit') == 1 or eval.count('error') == 1:
                            if re.search('2.0', eval):
                                if re.search('1.0', eval):
                                    crit_severity = True
                                    error_severity = True
                                else:
                                    crit_severity = True
                                    error_severity = False
                            elif re.search('1.0', eval):
                                crit_severity = False
                                error_severity = True
                for batch in lowMetricName['batches']:
                    batch['error_severity'] = error_severity
                    batch['crit_severity'] = crit_severity
    if jsonchick["lowMetrics"] != []:
        if jsonchick["dash_title"] == "" or  jsonchick["datasourse"] == "" or jsonchick["highMetric"] == "":
            return True
        for lowMetrics in jsonchick["lowMetrics"]:
            for batch in lowMetrics['batches']:
                if  batch['select'] == "" or batch['crit_sign'] == "" or batch['error_sign'] == "" or batch['crit_limit'] == "" or batch['error_limit'] == "" or batch['influxBank'] == "" or batch['crit_severity'] == [] or batch['error_severity'] == []:
                    print(json.dumps(jsonchick, indent = 4))
                    return True
    return jsonchick



def all_tics():
    filename = subprocess.Popen("ls -ltr /data/usnmp/Scripts_all_day/KAPACITOR/ | grep base | grep -v fmCouchbaseRebalaceErrorParams.tick | grep -v fmSsoCouchbase.tick | awk '{print$9}' | grep -v omplex | grep -v baseWebSsoErrorsParamsBank5 | grep -v baseCciMonDbParams | grep -v baseCciMonDbParams", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout.read().split('\n')[:-1]
    ticks = []
    no_fm = open('no_fm.txt', 'w')
    for base in filename:
        fm = re.sub('^base','fm', base)
        try:
            data1 = open('/data/usnmp/Scripts_all_day/KAPACITOR/' + fm, 'r').read()
            ticks.append({"base" : base, "fm" : fm})
        except:
            no_fm.write("no fm tick " + fm + "for base-tick " + base + "\n")
    return ticks


def __main__():
    ticks = all_tics()
    check = open('panels_for_check.log', 'w')
    trouble = open('trouble.log', 'w')
    log = open('create.log', 'w')
    crach_log = open('crash.log', 'w')
    ticks = [{'base': 'baseFileCountCDCVlgAvailabilityParams.tick', 'fm': 'fmFileCountCDCVlgAvailabilityParams.tick'}]
    for tick in ticks:
        tickes = tick['base'] + " " + tick['fm']
        log.write(tickes + "\n")
        try:
            log.write("\n" + "-------------"*5 + "\n")
            print(tickes)
            jsonchick = batch_json(tick)
            # print(json.dumps(jsonchick,sort_keys=True,indent=2))
            if jsonchick == True:
                crach_log.write(tickes + "\n")
                # crach_log.write("bad jsonchick")
                print("attantion!!!!! bad jsonchick")
                continue
            req, touble_panels = dashbord.create(jsonchick)
            print(req)
            log.write(json.dumps(req))
            if 'url' in req:
                for id in touble_panels:
                    url = req['url']
                    check.write(f"https://grafana.megafon.ru{url}?orgId=1&editPanel={id}" + "\n")
                    # print(f"https://grafana.megafon.ru{url}?orgId=1&editPanel={id}")
            else:
                # trouble.write("troubles on:  " +  tickes)
                crach_log.write(tickes + "\n")
        except Exception as err: 
            crach_log.write("----------------------" * 5)
            log.write(str(err))
            log.write("\n")
            crach_log.write(tickes + "\n")
            crach_log.write(str(err))
            crach_log.write("\n")
            print(err)

__main__()
