# -*- coding: utf-8 -*-
from freenom import Freenom

if __name__ == '__main__':
    freenom = Freenom('your username', 'your password')
    ###################################################
    pub_ip = freenom.getPublicIP()

    # add or modify a record
    freenom.setRecord('xxx.tk', '', 'a', pub_ip)
    freenom.setRecord('xxx.tk', 'www', 'a', pub_ip)

    # delete a record
    freenom.delRecord('xxx.tk', 'www')

    # show all records with domain
    freenom.showRecords('xxx.tk')