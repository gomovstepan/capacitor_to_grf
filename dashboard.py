#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import requests
import json
import re
import copy
import urllib3
import sqlparse
import sys
urllib3.disable_warnings()
sys.path.insert(0, '/data/usnmp/Scripts_all_day/step/convert_metrics')
import check_query



headers_test = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': '***********************'
        }

headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': '******************************'
    }


panels = {
    "aliasColors": {},
    "alert": {
            "alertRuleTags": {
                    "alertkey": [],
                    "severity": []
            },
            "conditions": [
                    {
                            "evaluator": {
                                    "params": [],
                                    "type": []
                            },
                            "operator": {
                                    "type": "and"
                            },
                            "query": {
                                    "params": [
                                            "A",
                                            "5m",
                                            "now"
                                    ]
                            },
                            "reducer": {
                                    "params": [],
                                    "type": "last"
                            },
                            "type": "query"
                    }
            ],
            "executionErrorState": "keep_state",
            "for": [],
            "frequency": "1m",
            "handler": 1,
            "name": [],
            "noDataState": "no_data",
            "notifications": []
    },
    "bars": False,
    "dashLength": 10,
    "dashes": False,
    "datasource": [],
    "fieldConfig": {
        "defaults": {},
        "overrides": []
    },
    "fill": 1,
    "fillGradient": 0,
    "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 1
    },
    "hiddenSeries": False,
    "id": [],
    "legend": {
        "alignAsTable": True,
        "avg": False,
        "current": True,
        "max": False,
        "min": False,
        "rightSide": True,
        "show": True,
        "total": False,
        "values": True
    },
    "lines": True,
    "linewidth": 1,
    "nullPointMode": "None",
    "options": {
        "alertThreshold": True
    },
    "percentage": False,
    "pluginVersion": "7.5.3",
    "pointradius": 2,
    "points": False,
    "renderer": "flot",
    "seriesOverrides": [],
    "spaceLength": 10,
    "stack": False,
    "steppedLine": False,
    "targets": [
        {
            "exemplar": True,
            "expr": [],
            "interval": "",
            "legendFormat": "{{__name__}} {{host}}",
            "queryType": "randomWalk",
            "refId": "A"
        }
    ],
    "thresholds": [],
    "timeFrom": None,
    "timeRegions": [],
    "timeShift": None,
    "title": [],
    "tooltip": {
        "shared": True,
        "sort": 0,
        "value_type": "individual"
    },
    "type": "graph",
    "xaxis": {
        "buckets": None,
        "mode": "time",
        "name": None,
        "show": True,
        "values": []
    },
    "yaxes": [
        {
            "format": "short",
            "label": None,
            "logBase": 1,
            "max": None,
            "min": None,
            "show": True
        },
        {
            "format": "short",
            "label": None,
            "logBase": 1,
            "max": None,
            "min": None,
            "show": True
        }
    ],
    "yaxis": {
        "align": False,
        "alignLevel": None
    }
}
alerts = {

}

dashboards= {
"dashboard": {
    "annotations": {
        "list": [
            {
                "builtIn": 1,
                "datasource": "-- Grafana --",
                "enable": True,
                "hide": True,
                "iconColor": "rgba(0, 211, 255, 1)",
                "name": "Annotations & Alerts",
                "type": "dashboard"
            }
        ]
    },
    "editable": True,
    "gnetId": None,
    "id": None,
    "graphTooltip": 0,
    "links": [],
    "panels": [],
    "schemaVersion": 27,
    "style": "dark",
    "tags": [],
    "templating": {
        "list": []
    },
    "time": {
        "from": "now-5m",
        "to": "now"
    },
    "timepicker": {},
    "timezone": "",
    "title": [],
    "uid": None,
    "version": {}
}
}



def OR_replace(tag):
    counter = 0
    hashs = ""
    for pis in tag.split('"'):
        if counter == 0:
            hashs = pis + ' "'
        if counter%2 != 0:
            hashs += pis + "|"
        counter +=1
    i = hashs[:-1] + '"'
    if re.search(' = ',i):
        i = i.replace('=', '=~')
    i = i.replace('\(','').replace('\)','')
    return(i)


def prmql_query(query,title):
    query = query.replace('"ret_30w".',"").split("GROUP BY")[0].split("group by")[0].split('AND $timeFilter')[0].replace('$timeFilter and',"").replace('$timeFilter AND',"").replace('$timeFilter',"")
    metric = ""
    try:
        query = query.replace("from","FROM").replace("where","WHERE").replace('WHERE 1=1 AND','WHERE').replace('WHERE 1=1',"WHERE")
        mes = query.split("FROM")[1].split("WHERE")[0]
        mes = mes.replace('"','').replace('(','').replace(')','').replace(' ','')
        tag = query.split("WHERE")[1].replace('"','').replace("'",'"').replace(' and',',').replace(' AND',',').replace("|", ".*|.*").replace('st,','stand').replace('\\','').replace('WHERE 1=1 AND','WHERE').replace('WHERE 1=1',"WHERE")
        tag = tag + "}"
        field = query.split('FROM')[0].split('from')[0].replace("SELECT","").replace("select","").replace("non_negative_derivative(","irate(").replace("non_negative_difference(","increase(").replace("difference(","idelta(").replace("sum(","sum(").replace("min(","min_over_time(").replace("max(","max_over_time(").replace("mean(","avg_over_time(").replace("derivative(","deriv(").replace('\n', ' ')
        field1 = ""
        if re.search("AS",field):
            cnt = 0
            for fld in field.split('AS'):
                if cnt == 0:
                    field1 = fld
                if re.search(',',fld):
                    if cnt != 0:
                        field1 += "," + fld.split(',')[1]
                cnt += 1
        if re.search(" as",field):
            cnt = 0
            for fld in field.split(' as'):
                if cnt == 0:
                    field1 = fld
                if re.search(',',fld):
                    if cnt != 0:
                        if re.search('"',fld):
                            field1 = fld.split('"')[1].split('"')[0]
                        else:
                            field1 += "," + fld.split(',')[1]
                cnt += 1
        if field1 != "":
            field = field1
        tag2 = ""
        for i in tag.split(','):
            flag = False
            if re.search(" //", i):
                continue
            if (not re.search('server',i) and not re.search('api',i) and not re.search('directory',i) and not re.search('pid_file',i) and not re.search('path',i)) and not re.search('eapi',i) and not re.search('oapi',i):
                counter = 0
                if (re.search("= ",i) or re.search('="',i) or re.search('=  ',i)) and not re.search(" or ",i) and not re.search(" OR ",i):
                    counter = 0
                    tagot = ""
                    i = i.replace('=','=~ ')
                    for k in i.split('"'):
                        counter +=1
                        if counter%2 == 0:
                            k = '"' + k + '.*"'
                        tagot += k
                    tag2 += tagot + ","
                    flag = True
                if re.search(" OR ",i) or re.search(" or ",i):
                    flag = True
                    tagot = OR_replace(i)
                    tag2 += tagot + ","
                    flag = True 
                if flag == False:
                    for k in i.split("/"):
                        counter +=1
                        if counter%2 == 0:
                            k = '".*' + k + '.*"'
                        tag2 += k
                    tag2 += ","
                    flag = True
            if re.search('server',i) or re.search('api',i) or re.search('directory',i) or re.search('pid_file',i) or re.search('path',i):
                i = i.replace(' /', ' ".*').replace('/ ', '.*"').replace('/}', '.*"}')
            if  re.search("\$",i) and not re.search('server',i) and not re.search('directory',i):
                i = i.replace("/^",'"').replace('$/','"').replace('/$','".*$').replace('/','.*"')
                if re.search(" OR ",i) or re.search(" or ",i):
                    flag = True
                    i = OR_replace(i)
                    tag2 += i + ","
            if flag == False:
                if re.search(" OR ",i) or re.search(" or ",i):
                    flag = True
                    i = OR_replace(i) + '"'
                    tag2 += i + ","
                else:
                    tag2 += i + ","
        tag2 = "{" + tag2[:-1] + "}"
        if not re.search("\(",field):
            field = '" ' + field.replace('"','').replace(" ","") + '"'
            metric = field.replace('" ',f'{mes}_').replace('"', f'{tag2}')
        else:
            if re.search('"\)',field):
                metric = field.replace('("',f'({mes}_').replace('")', f'{tag2})')
            else:
                metric = field.replace('"','').replace('(',f'({mes}_').replace(')', f'{tag2})')
        metric = agregation(metric)
    except:
        metric = False
    metric = metric.replace('!=~','!~')
    eval = re.findall(r'[=~!] (\d+).*', metric)
    if len(eval) > 0:
        for i in eval:
            new = '"' + i + '"'
            metric = metric.replace(i,new)
    if re.search("cpu_usage_active",metric) or re.search("mem_used_percent",metric) or re.search("disk_used_percenrt",metric) or re.search("sysmon",metric):
        iti_metric = open('iti_metrics.log', 'a')
        iti_metric.write(title + "  " + metric + "\n")
    return metric

def agregation(metric):
    metric = metric.replace("last(","(").replace(".*.*", ".*").replace('""', '"').replace('  ', ' ').replace("~~", "~").replace("{  ,","{").replace("{ ,","{").replace("{,","{").replace("}}","}").replace('{ (','{ ').replace(') }',' }').replace('.*.-','.*-').replace('..','.').replace(' /.','".*').replace('./','.*"').replace("percentile","quantile_over_time").replace('^','').replace('$.*','.*').replace('} "}', '}').replace("{ 1=1 }", "{}").replace('" , (', '", ').replace('}.*"})','})')
    if re.search('}',metric) != -1 and re.search('{',metric) == -1:
        metric = metric.replace('}', '')
    return metric


def create(jsonch):
    x = 0
    y = 0
    dashboard = copy.deepcopy(dashboards)
    dashboard['dashboard']['title'] = jsonch['dash_title']
    id = 1
    alert = False
    touble_panels = []
    for lowMetric in jsonch['lowMetrics']:
        title = lowMetric['name']
        id += 1
        y = 0
        for batch in lowMetric['batches']:
            if batch['crit_severity'] == True:
                change_datasource = False
                panel = copy.deepcopy(panels)
                for q in panel['targets']:
                    legendFormat = """{{__name__}}"""
                    select = batch['select']
                    select = select.replace('\n',' ').replace('  ',' ').replace("'''+db+'.'+rp+'''.",'').replace('1=1 AND', '').replace('AS value ', '').replace('\/','/')
                    query = prmql_query(select,title)
                    if re.search('sysmonDiskTable_sysmonDiskUsedPct',query):
                        query = query.replace('sysmonDiskTable_sysmonDiskUsedPct', 'disk_used_percent').replace('sysmonDiskPath','path')
                        change_datasource = True
                    eval = re.findall(r'= (\d+) .*', query)
                    if len(eval) > 0:
                        for i in eval:
                            new = '"' + i + '"'
                            query = query.replace(i,new)
                    alert = check_query.check_queries(select, query, batch['influxBank'])
                    # if re.search('disk_used_percent', query) or re.search('mem_used_percent', query) or re.search('cpu_usage_active', query):
                    #     append_panel = False
                    groupBy = batch['groupBy']
                    if re.search(' sum',query):
                        if groupBy != '' and groupBy != '*':
                            query = query.replace(' sum(', f'sum by ({groupBy}) (')
                    if re.search(' avg_over_time',query):
                        if groupBy != '' and groupBy != '*':
                            query = query.replace(' avg_over_time(', f'avg_over_time by ({groupBy}) (')
                    if batch['groupBy'] != "*" or batch['groupBy'] != "":
                        for tag in batch['groupBy'].split(','):
                            legendFormat += " " + "{{" + tag + "}}"
                    q['expr'] = query
                    q['inerval'] = batch['crit_minstep']
                    q['groupBy'] = legendFormat
                if change_datasource == True:
                    panel['datasource'] = "Prometheus (prod)"
                    batch['crit_limit'] = int(batch['crit_limit'])
                    if batch['crit_limit'] > 100:
                        batch['crit_limit'] = batch['crit_limit'] / 100
                else:
                    panel['datasource'] = jsonch['datasourse']
                panel['title'] = title                    
                panel['alert']['for'] = batch['crit_duration']
                panel['alert']['name'] = title
                panel['alert']['alertRuleTags']['alertkey'] = str(jsonch['highMetric']) + "GF"
                panel['alert']['alertRuleTags']['severity'] = "critical"
                for conditions in panel['alert']['conditions']: # допилить
                    conditions['evaluator']['params'] = [int(batch['crit_limit'])]
                    if batch['crit_sign'] == "<":
                        conditions['evaluator']['type'] = "lt"
                    elif batch['crit_sign'] == ">":
                        conditions['evaluator']['type'] = "gt"
                    elif batch['crit_sign'] == "!=":
                        conditions['evaluator']['type'] = "outside_range"
                        conditions['evaluator']['params'] = [int(batch['crit_limit']),int(batch['crit_limit'])]
                    elif batch['crit_sign'] == "==":
                        conditions['evaluator']['type'] = "within_range"
                        conditions['evaluator']['params'] = [int(batch['crit_limit'])-1,int(batch['crit_limit'])+1]
                    elif batch['crit_sign'] == ">=":
                        conditions['evaluator']['type'] = "gt"
                        conditions['evaluator']['params'] = [int(batch['crit_limit']) - 1]
                    elif batch['crit_sign'] == "<=":
                        conditions['evaluator']['type'] = "lt"
                        conditions['evaluator']['params'] = [int(batch['crit_limit']) + 1]
                    else:
                        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'*8)
                id += 1
                panel['id'] = id
                panel['gridPos']['y'] = y
                panel['gridPos']['x'] = x
                panel['description'] = select
                x = x + 12
                y = y + 9
                if x >= 24:
                        x = 0
                # if append_panel == True:
                if alert == True:
                    touble_panels.append(id)
                dashboard['dashboard']['panels'].append(panel)
            if batch['error_severity'] == True:
                change_datasource = False
                panel = copy.deepcopy(panels)
                for q in panel['targets']:
                    legendFormat = """{{__name__}}"""
                    select = batch['select']
                    select = select.replace('\n',' ').replace('  ',' ').replace("'''+db+'.'+rp+'''.",'').replace('1=1 AND', '').replace('AS value ', '').replace('\/','/')
                    query = prmql_query(select,title)
                    if re.search('sysmonDiskTable_sysmonDiskUsedPct',query):
                        query = query.replace('sysmonDiskTable_sysmonDiskUsedPct', 'disk_used_percent').replace('sysmonDiskPath','path')
                        change_datasource = True
                    alert = check_query.check_queries(select, query, batch['influxBank'])
                    # if re.search('disk_used_percent', query) or re.search('mem_used_percent', query) or re.search('cpu_usage_active', query):
                    #     append_panel = False
                    groupBy = batch['groupBy']
                    if re.search(' sum',query):
                        if groupBy != '' and groupBy != '*':
                            query = query.replace(' sum(', f'sum by ({groupBy}) (')
                    if re.search(' avg_over_time',query):
                        if groupBy != '' and groupBy != '*':
                            query = query.replace(' avg_over_time(', f'avg_over_time by ({groupBy}) (')
                    if batch['groupBy'] != "*" or batch['groupBy'] != "":
                        for tag in batch['groupBy'].split(','):
                            legendFormat += " " + "{{" + tag + "}}"
                    q['expr'] = query
                    q['inerval'] = batch['error_minstep']
                    q['groupBy'] = legendFormat
                if change_datasource == True:
                    panel['datasource'] = "Prometheus (prod)"
                    batch['error_limit'] = int(batch['error_limit'])
                    if batch['error_limit'] > 100:
                        batch['error_limit'] = batch['error_limit'] / 100
                else:
                    panel['datasource'] = jsonch['datasourse']
                panel['title'] = title
                panel['alert']['for'] = batch['error_duration']
                panel['alert']['name'] = title
                panel['alert']['alertRuleTags']['alertkey'] = str(jsonch['highMetric']) + "GF"
                panel['alert']['alertRuleTags']['severity'] = "error"
                for conditions in panel['alert']['conditions']:
                    conditions['evaluator']['params'] = [int(batch['error_limit'])]
                    if batch['error_sign'] == "<":
                        conditions['evaluator']['type'] = "lt"
                    elif batch['error_sign'] == ">":
                        conditions['evaluator']['type'] = "gt"
                    elif batch['error_sign'] == "!=":
                        conditions['evaluator']['type'] = "outside_range"
                        conditions['evaluator']['params'] = [int(batch['error_limit']),int(batch['error_limit'])]
                    elif batch['error_sign'] == "==":
                        conditions['evaluator']['type'] = "within_range"
                        conditions['evaluator']['params'] = [int(batch['error_limit'])-1,int(batch['error_limit'])+1]
                    elif batch['error_sign'] == ">=":
                        conditions['evaluator']['type'] = "gt"
                        conditions['evaluator']['params'] = [int(batch['error_limit']) + 1]
                    elif batch['error_sign'] == "<=":
                        conditions['evaluator']['type'] = "lt"
                        conditions['evaluator']['params'] = [int(batch['error_limit']) + 1]
                    else:
                        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'*8)
                id += 1
                panel['id'] = id
                panel['gridPos']['y'] = y
                panel['gridPos']['x'] = x
                panel['description'] = select
                x = x + 12
                y = y + 9
                if x >= 24:
                        x = 0
                # if append_panel == True:
                if alert == True:
                    touble_panels.append(id)
                dashboard['dashboard']['panels'].append(panel)
    dashboard['dashboard']['uid'] = None
    dashboard['dashboard']['id'] = None
    dashboard['dashboard']['gnetId'] = None
    dashboard['dashboard']['editable'] = True
    # dashboard['folderId'] = 8518
    # dashboard['folderUid'] = 'NM6rGiJnk'
    dashboard['folderId'] = 8588
    dashboard['folderUid'] = 'kHbT-FJ7z'
    dashboard['dashboard']['overwrite'] = False
    data = json.dumps((dashboard), indent=2)
    req = requests.post('https://grafana.megafon.ru/api/dashboards/db', headers=headers, data=data, verify=False)
    # req = requests.post('https://grafana-test.megafon.ru/api/dashboards/db', headers=headers_test, data=data, verify=False)
    req = req.json()
    # req = ""
    if 'message' in req:
        print(dashboard['dashboard']['title'])   
        print(req['message'])     
    return req, touble_panels
        # return data

