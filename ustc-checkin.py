#!/usr/bin/python3

import os
import re
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

CAS_LOGIN_URL = "https://passport.ustc.edu.cn/login"
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
REPORT_URL = "https://weixine.ustc.edu.cn/2020/daliy_report"
# Not my fault:                                  ^^

print("Tsinghua University Daily Health Report")

retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=retries))
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
s.get(CAS_LOGIN_URL, params={"service": CAS_RETURN_URL})

# Send CAS credentials
r = s.post("https://passport.ustc.edu.cn/login", data={
    "model": "uplogin.jsp",
    "service": CAS_RETURN_URL,
    "warn": "",
    "showCode": "",
    "username": os.environ["USERNAME"],
    "password": os.environ["PASSWORD"],
    "button": "",
})

# Parse the "_token" key out
x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
token = re.search(r'value="(\w*)"', x).group(1)
r = s.post(REPORT_URL, data={
    "_token": token,
    "now_address": "1",
    "gps_now_address": "",
    "now_province": "340000",
    "gps_province": "",
    "now_city": "340100",
    "gps_city": "",
    "now_detail": "",
    "is_inschool": "4",
    "body_condition": "1",
    "body_condition_detail": "",
    "now_status": "1",
    "now_status_detail": "",
    "has_fever": "0",
    "last_touch_sars": "0",
    "last_touch_sars_date": "",
    "last_touch_sars_detail": "",
    "last_touch_hubei": "0",
    "last_touch_hubei_date": "",
    "last_touch_hubei_detail": "",
    "last_cross_hubei": "0",
    "last_cross_hubei_date": "",
    "last_cross_hubei_detail": "",
    "return_dest": "1",
    "return_dest_detail": "",
    "other_detail": "",
})

# Fail if not 200
r.raise_for_status()

# Fail if not reported
assert r.text.find("上报成功") >= 0
