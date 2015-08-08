# -*- coding: utf-8 -*-
from __future__ import print_function
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import hashlib
import xml.etree.ElementTree as ET
import time
from config import TOKEN

# Create your views here.
TOKEN = TOKEN


@csrf_exempt
def index(request):
    if request.method == "GET":
        global TOKEN
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echoStr = request.GET.get('echostr', None)

        token = TOKEN

        tmpList = [token, timestamp, nonce]
        tmpList.sort()

        tmp_str = "%s%s%s" % tuple(tmpList)
        tmp_str = hashlib.sha1(tmp_str).hexdigest()

        if tmp_str == signature:
            return HttpResponse(echoStr)
        else:
            return HttpResponse('Error')
    elif request.method == "POST":
        xml_msg = request.body
        response = HttpResponse(response_msg(xml_msg), content_type="application/xml")
        return response


MSG_TYPE_TEXT = "text"


def response_msg(msg):
    tree = ET.fromstring(msg)
    msg = parse_xml(tree)

    res = ""
    if msg['MsgType'] == MSG_TYPE_TEXT:
        reply_content = "Hello"
        res = get_reply_xml(msg, reply_content)

    return res


def get_reply_xml(msg, reply_content):
    template = '''
        <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
        </xml>
    '''

    res = template % (msg['FromUserName'], msg['ToUserName'], str(int(time.time())), 'text', reply_content)

    return res


def parse_xml(root_elm):
    """
    :param root_elm:
    :return: msg dict
    """
    msg = {}
    if root_elm.tag == 'xml':
        for child in root_elm:
            msg[child.tag] = child.text
    return msg
