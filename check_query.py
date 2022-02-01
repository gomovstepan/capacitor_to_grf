#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import re
from typing import no_type_check
import json
from requests.api import request
import urllib3
urllib3.disable_warnings()

headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': '*************************'
    }

proxies = {"http":"*********", "https":"*******************"}

# influxql_metric = """SELECT last("running") FROM "procstat_lookup" WHERE  "host" =~ /(dv|kvk|msk|nw|sib|url|vlg)-lbrt-app0[12]/  AND "zone" = 'GF'  AND "stand" = 'GF'  AND "appl_id" = '8098'"""
# promql_metric = """ (procstat_lookup_running{ host =~ ".*(dv.*|.*kvk.*|.*msk.*|.*nw.*|.*sib.*|.*url.*|.*vlg)-lbrt-app0[12].*" , zone = "GF" , stand = "GF" , appl_id = "8098" })"""
# datasource = "telegraf"

def check_queries(influxql_metric, promql_metric, datasource):
    http = urllib3.PoolManager()
    # influxql_request = ""
    norm_db = False
    if datasource == "telegraf":
        influxql_request  = http.request('GET', f"https://grafana.megafon.ru/api/datasources/proxy/459/query?db=telegraf&q={influxql_metric}", headers = headers)
        norm_db = True
    if datasource == "mondb":
        influxql_request  = http.request('GET', f"https://grafana.megafon.ru/api/datasources/proxy/277/query?db=mondb&q={influxql_metric}", headers = headers)
        norm_db = True
    if datasource == "snmp_int":
        influxql_request  = http.request('GET', f"https://grafana.megafon.ru/api/datasources/proxy/324/query?db=snmp_int&q={influxql_metric}", headers = headers)
        norm_db = True
    promql_request = http.request('GET', f"https://grafana.megafon.ru/api/datasources/proxy/891/api/v1/query_range?query={promql_metric}", headers = headers)
    alert = False
    if promql_request.status != 200 or influxql_request.status != 200:
        alert = True
    if 'data' in json.loads(promql_request.data):
        if json.loads(promql_request.data)['data']['result'] == []:
            alert = True
    else:
        print("--------------" * 5)
        print(json.loads(promql_request.data))
        print(promql_metric)
        print(influxql_metric)
        alert = True
    try:
        for i in json.loads(influxql_request.data)['results']:
            for val in i['series']:
                var = val['values']
    except:
        alert = True
    if norm_db == False:
        alert = True
    return alert