Freenom-dns Script
========================
An unofficial python implementation for managing freenom.com dns records.

## Freenom
Freenom is the world's first and only free domain provider.
## Install
```
pipenv install
```
## How to use
```python
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
```
## print results
```
LoggedIn: *True
PublicIP: *xxx.xxx.xxx.xxx
setRecord: **Record added successfully
setRecord: **Record added successfully
*
-------------------showRecords-------------------
['', 'A', '3600', 'xxx.xxx.xxx.xxx']
['WWW', 'A', '3600', 'xxx.xxx.xxx.xxx']
```
## License
[MIT](https://github.com/PunkLee2py/freenom-dns/blob/master/LICENSE)