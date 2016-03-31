#coding=utf8
import requests
import json
from hera import hera_app
from common.models import HeraTask
from common.util import logger
from common.util import sprintf_result

from common.exceptions import IncorrectHttpResponseCode

import task_controller

@hera_app.task
def hello_world(my_name):
    print 'timer hello world', my_name


@hera_app.task(bind=True, base=HeraTask)
# def register_callback(self, cb_url, cb_method='get', **kwargs):
# TODO 与任务数据无关的argument,或者任务参数不是比传的可变性参数,应该使用kwargs:   sen_task('blalbla', kwargs={'a': a, 'b': 2})
# 也不是必要, 就是优雅一点,省的满地的None占位符
def register_callback(self, url, method='get', data=None, params=None, retry_args=None, **kwargs):
    timeout = kwargs.get('timeout') or 1
    cb_method = method.lower()
    cb_url = url.lower()
    logger.debug('receive callback: {} {} {} {} {}'.format(cb_url, cb_method, data, params, timeout))
    err = None
    exc = None
    response = None
    try:
        response = getattr(requests, cb_method)(
            cb_url, data=data, params=params, timeout=timeout, allow_redirects=False)
    except requests.ConnectionError as e:
        exc = e
        err = "timer execute callback connect failed, url: {}, err: {}".format(cb_url, e.message)
    except requests.Timeout as e:
        exc = e
        err = "timer execute callback timeout, url: {}, err: {}".format(cb_url, e.message)
    except Exception as e:
        exc = e
        err = "timer execute callback failed, url: {}, err: {}".format(cb_url, e.message)

    if err:
        logger.error(err)
        # NOTIC: retry maybe distribute to other node
        return self.retry(exc=exc, retry_args=retry_args)
    elif response.status_code != 200:
        return self.retry(exc=IncorrectHttpResponseCode("http response not 200"), retry_args=retry_args)
    else:
        return sprintf_result(response, self.request.retries)

@hera_app.task(bind=True, base=HeraTask)
def register_callback_v2(self, kwargs):
    print kwargs, type(kwargs)
    # kwargs = json.loads(kwargs)
    method = kwargs.get('method', 'get')
    url = kwargs['url']
    data = kwargs.get('data')
    params = kwargs.get('params')
    retry_args = kwargs.get('retry_args', [])
    timeout = kwargs.get('timeout', 1)
    require_json_res = kwargs.get('require_json_res', False)  # some url hide by nginx, maybe got 200 status beacuse ngx redirect
    logger.debug('receive callback: {} {} {} {} {}'.format(url, method, data, params, timeout))
    err = None
    exc = None
    response = None
    try:
        response = getattr(requests, method)(
            url, data=data, params=params, timeout=timeout, allow_redirects=False)
    except requests.ConnectionError as e:
        exc = e
        err = "timer execute callback connect failed, url: {}, err: {}"
    except requests.Timeout as e:
        exc = e
        err = "timer execute callback timeout, url: {}, err: {}"
    except Exception as e:
        exc = e
        err = "timer execute callback failed, url: {}, err: {}"

    if err:
        logger.error(err.format(url, exc.message))
        # NOTIC: retry maybe distribute to other node
        return self.retry(exc=exc, retry_args=retry_args)
    elif require_json_res and response.status_code == 200:
        try:
            json.loads(response.text)
        except Exception, e:
            return self.retry(exc=e, retry_args=retry_args)
        else:
            return sprintf_result(response, self.request.retries)
    elif response.status_code != 200:
        return self.retry(exc=IncorrectHttpResponseCode("http response not 200"), retry_args=retry_args)
    else:
        return sprintf_result(response, self.request.retries)


@hera_app.task()
def revoke_manual(task_id, terminate=True):
    task_controller.revoke_manual(task_id, terminate)
