# -*- coding: utf-8 -*-
from freenom import Freenom

if __name__ == '__main__':
    freenom = Freenom('18683833822@163.com', '496709219')
    ###################################################
    pub_ip = freenom.getPublicIP()

    # add or modify a record
    freenom.setRecord('wagger2.ga', '', 'a', pub_ip)
    freenom.setRecord('wagger2.ga', 'www', 'a', pub_ip)
    freenom.setRecord('wagger2.ga', 'asd', 'a', '192.168.123.111')

    # delete a record
    freenom.delRecord('wagger2.ga', 'asd')

    # show all records with domain
    freenom.showRecords('wagger2.ga')


