
from error import UnAuthorizedException
from error import BadRequestBodyException
from error import UnavailableServiceError
from error import UnexpectedStatusException
from error import InternalServerError   
from error import UnAvaliableResourceException
from error import ProjectExistException
from error import NotAllowedException
from error import SameNameDocumentException
from rest.client import RestClient

import json

__all__ = (
        "Service",
   )

class Service(object):
    _fields = []

    def __init__(self,*args,**kargs):
        for name,val in zip(self._fields,args):
            setattr(self,name,val)
        for key, value in kargs.iteritems():
            setattr(self,key,value)
        self.restclient = RestClient(self.base_url)

    def messages(self,res,content,extra_msg=None):
        if res['status'] == '200' or res['status'] == '304':
            rst = None
            if extra_msg:
                raise ProjectExistException('Status 200', extra_msg)
            try:
                rst = json.loads(content)
            except ValueError, e:
                if content.strip() == "":
                    return rst
                print "Exception while decoding", e ,"its may due to file already exists on the server or not a PO file "
                return rst
            return rst
        elif res['status'] == '201':
            return True
        elif res['status'] == '401':
            raise UnAuthorizedException('Error 401', 
                                        'This operation is not authorized, please check username and apikey')
        elif res['status'] == '400':
            raise BadRequestBodyException('Error 400', content)
        elif res['status'] == '404':
            raise UnAvaliableResourceException('Error 404', 
                                               'The requested resource/project is not available')
        elif res['status'] == '405':
            raise NotAllowedException('Error 405', 
                                      'The requested method is not allowed')
        elif res['status'] == '409':
            raise SameNameDocumentException('Error 409', 'A document with same name already exists.')
        elif res['status'] == '500':
            raise InternalServerError('Error 500', content)
        elif res['status'] == '503':
            raise UnavailableServiceError('Error 503', 
                                          'Service Temporarily Unavailable, stop processing!')
        else:
            raise UnexpectedStatusException('Error', 
                                            'Unexpected Status (%s), failed to push: %s' % (res['status'], extra_msg or ""))
