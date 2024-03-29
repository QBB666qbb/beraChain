# -*- coding: utf-8 -*-
# Time     :2024/1/19 21:38
# Author   :ym
# File     :utils.py
import time
from typing import Union

import requests
from loguru import logger


def get_yescaptcha_google_token(yes_captcha_client_key: str) -> Union[bool, str]:
    json_data = {"clientKey": yes_captcha_client_key,
                 "task": {"websiteURL": "https://artio.faucet.berachain.com/",
                          "websiteKey": "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
                          "type": "RecaptchaV3TaskProxylessM1S7", "pageAction": "submit"}, "softID": 109}
    response = requests.post(url='https://api.yescaptcha.com/createTask', json=json_data).json()
    if response['errorId'] != 0:
        raise ValueError(response)
    task_id = response['taskId']
    time.sleep(5)
    for _ in range(30):
        data = {"clientKey": yes_captcha_client_key, "taskId": task_id}
        response = requests.post(url='https://api.yescaptcha.com/getTaskResult', json=data).json()
        if response['status'] == 'ready':
            return response['solution']['gRecaptchaResponse']
        else:
            time.sleep(2)
    logger.warning(response)
    return False


def get_no_captcha_google_token(no_captcha_api_token: str) -> Union[bool, str]:
    headers = {'User-Token': no_captcha_api_token, 'Content-Type': 'application/json', 'Developer-Id': 'UTtF29'}
    json_data = {'sitekey': "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
                 'referer': 'https://artio.faucet.berachain.com/', 'size': 'invisible', 'title': 'Berachain Faucet',
                 'action': 'submit', 'internal': False}
    response = requests.post(url='http://api.nocaptcha.io/api/wanda/recaptcha/universal', headers=headers,
                             json=json_data).json()
    if response.get('status') == 1:
        if response.get('msg') == '验证成功':
            return response['data']['token']
    logger.warning(response)
    return False


def get_2captcha_google_token(captcha_key: str) -> Union[bool, str]:
    params = {'key': captcha_key, 'method': 'userrecaptcha', 'version': 'v3', 'action': 'submit', 'min_score': 0.5,
              'googlekey': '6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH', 'pageurl': 'https://artio.faucet.berachain.com/',
              'json': 1}
    response = requests.get(f'https://2captcha.com/in.php?', params=params).json()
    if response['status'] != 1:
        raise ValueError(response)
    task_id = response['request']
    for _ in range(60):
        response = requests.get(f'https://2captcha.com/res.php?key={captcha_key}&action=get&id={task_id}&json=1').json()
        if response['status'] == 1:
            return response['request']
        else:
            time.sleep(3)
    return False


def claim_bera(pk):
    """
    领水函数
    :param pk: 钱包私钥
    :return: 无
    """

    ac = Account.from_key(pk)  # 账户3

    client_key = '1d137118bce28d88bff8ba9260597ab9efbd7caa38177'
    bera = BeraChainTools(private_key=ac.key, client_key=client_key, solver_provider='yescaptcha',
                          rpc_url='https://rpc.ankr.com/berachain_testnet')
    # 不使用代理
    result = bera.claim_bera()
    logger.debug(result.text)


def add_liquidity(pk2):
    account = Account.from_key(pk2)
    bera = BeraChainTools(private_key=account.key, solver_provider='yescaptcha',
                          rpc_url='https://rpc.ankr.com/berachain_testnet')

    # # bex 使用bera交换usdc
    # bera_balance = bera.w3.eth.get_balance(account.address)
    # bera1 = bera.w3.from_wei(bera_balance, 'ether')
    # print(f'The balance is: {bera1} bera')
    # logger.info(bera_balance)
    # result = bera.bex_swap(int(bera_balance * 0.2), wbear_address, usdc_address)
    # logger.debug(result)

    # # 授权usdc
    # approve_result = bera.approve_token(bex_approve_liquidity_address, int("0x" + "f" * 64, 16), usdc_address)
    # logger.debug(approve_result)
    # # # bex 增加 usdc 流动性
    # usdc_balance = bera.usdc_contract.functions.balanceOf(account.address).call()
    # result = bera.bex_add_liquidity(int(usdc_balance * 0.5), usdc_pool_liquidity_address, usdc_address)
    # logger.debug(result)


if __name__ == '__main__':
    from eth_account import Account
    from loguru import logger

    from bera_tools import BeraChainTools
    from config.address_config import (
        usdc_address, wbear_address, bex_approve_liquidity_address,
        usdc_pool_liquidity_address, client_key
    )

    pk = "92b87f6cacf6cc8b8a70eaa8df93ce71d870e3affe8c7ea6739a7deca657b749" # 账户私钥

    account = Account.from_key(pk)
    bera = BeraChainTools(private_key=account.key, client_key=client_key, solver_provider='yescaptcha',
                          rpc_url='https://rpc.ankr.com/berachain_testnet')

    # result = bera.claim_bera()
    # logger.debug(result.text)

    # bex 使用bera交换usdc
    # bera_balance = bera.w3.eth.get_balance(account.address)
    # logger.info(bera_balance)
    # result = bera.bex_swap(int(bera_balance * 0.5), wbear_address, usdc_address)
    # logger.debug(result)

    # # 授权usdc
    approve_result = bera.approve_token(bex_approve_liquidity_address, int("0x" + "f" * 64, 16), usdc_address)
    logger.debug(approve_result)
    # # bex 增加 usdc 流动性
    usdc_balance = bera.usdc_contract.functions.balanceOf(account.address).call()
    result = bera.bex_add_liquidity(int(usdc_balance * 0.8), usdc_pool_liquidity_address, usdc_address)
    logger.debug(result)



