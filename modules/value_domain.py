import os
import json
import pathlib        
import datetime
import requests

# Logger setting
from logging import getLogger, FileHandler, DEBUG
logger = getLogger(__name__)
today = datetime.datetime.now()
handler = FileHandler(f'log/{today.strftime("%Y-%m-%d")}_result.log', mode='a')
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

### functions ###
def parse_body(results):
    for domain in results:
        expiration_date = domain["expirationdate"].replace('-', '/')
        edate = datetime.datetime.strptime(expiration_date, "%Y/%m/%d")
        if datetime.date(edate.year, edate.month, edate.day) < datetime.date.today():
            continue
        autorenew_target = "-"
        if domain["autorenew"] == 1:
            autorenew_target = f'=IF(COUNTIF(\'ドメイン自動更新管理\'!B4:B63, "{domain["domainname"]}"), "対象", "対象外")'
        yield [domain["domainname"], "バリュー", expiration_date, domain["autorenew"], autorenew_target]

def get_list_number(value_domain_url, headers):
    try:
        req = requests.get(value_domain_url, headers=headers)
        body = req.json()
        list_number = body["paging"]["max"]
        logger.debug(f'value_domain: list_number: {list_number}')
        return list_number
    except Exception as err:
        logger.error(f'Error: value_domain: get_list_number: {err}')
        return None

def get_domain_info():
    value_domain_url = "https://api.value-domain.com/v1/domains"
    api_key = os.environ["VALUE_DOMAIN_API_KEY"]
    headers = {'Authorization': f'Bearer {api_key}'}
    list_number = get_list_number(value_domain_url, headers)
    if not list_number:
        return None
    try:
        req = requests.get(f'{value_domain_url}?limit={list_number}', headers=headers)
        body = req.json()
        domain_info = list(parse_body(body['results']))
        logger.debug(f'value_domain: total_list_number: {len(domain_info)}')
        return domain_info
    except Exception as err:
        logger.error(f'Error: value_domain: get_domain_info: {err}')
        return None
