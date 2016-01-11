
from error import UnAuthorizedException
from error import BadRequestBodyException
from error import UnavailableServiceError
from error import UnexpectedStatusException
from error import InternalServerError
from error import UnAvaliableResourceException
from error import ProjectExistException
from error import NotAllowedException
from error import SameNameDocumentException
from error import ForbiddenException
from rest.client import RestClient
from projectutils import ToolBox

import json
import sys

__all__ = (
    "Service",
)


EXCEPTION_STATUS_DICT = {
    '401': (UnAuthorizedException, 'Error 401', 'This operation is not authorized, please check username and apikey'),
    '400': (BadRequestBodyException, 'Error 400', 'Request body not appropriate'),
    '404': (UnAvaliableResourceException, 'Error 404', 'The requested resource/project is not available'),
    '405': (NotAllowedException, 'Error 405', 'The requested method is not allowed'),
    '409': (SameNameDocumentException, 'Error 409', 'A document with same name already exists'),
    '500': (InternalServerError, 'Error 500', 'Internel Server Error'),
    '503': (UnavailableServiceError, 'Error 503', 'Service Temporarily Unavailable, stop processing'),
    '403': (ForbiddenException, 'Error 403',
            'You are authenticated but do not have the permission for the requested resource'),
}


class Service(object):
    _fields = []

    def __init__(self, *args, **kargs):
        for name, val in zip(self._fields, args):
            setattr(self, name, val)
        for key, value in kargs.iteritems():
            setattr(self, key, value)
        self.restclient = RestClient(self.base_url)

    def excption_handler(self, exception_class, error, error_msg):
        try:
            raise exception_class(error, error_msg)
        except exception_class as e:
            print '', e
        finally:
            sys.exit(1)

    def messages(self, res, content, extra_msg=None):
        if res['status'] == '200' or res['status'] == '304':
            rst = None
            if extra_msg:
                raise ProjectExistException('Status 200', extra_msg)
            try:
                rst = ToolBox.xmlstring2dict(content) \
                    if res.get('content-type') and 'xml' in res['content-type'] else json.loads(content)
            except ValueError, e:
                if content.strip() == "":
                    return rst
                print "Exception while decoding", e, "its may due to file already exists on the server or not a PO file "
                return rst
            return rst
        elif res['status'] == '201':
            return True
        elif res['status'] in EXCEPTION_STATUS_DICT:
            self.excption_handler(*EXCEPTION_STATUS_DICT[res['status']])
        else:
            self.excption_handler(UnexpectedStatusException,
                                  'Error', 'Unexpected Status (%s), failed to push: %s' % (res['status'], extra_msg or ""))
