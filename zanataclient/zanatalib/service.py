
import json
import sys

from zanataclient.zanatalib.error import (
    BadRequestBodyException,
    ForbiddenException,
    InternalServerError,
    NotAllowedException,
    ProjectExistException,
    SameNameDocumentException,
    UnAuthorizedException,
    UnAvaliableResourceException,
    UnavailableServiceError,
    UnexpectedStatusException,
)
from zanataclient.zanatalib.projectutils import ToolBox

from zanataclient.zanatalib.rest.client import RestClient
from zanataclient.zanatalib.rest.config import media_types


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
        for key, value in kargs.items():
            setattr(self, key, value)
        self.restclient = RestClient(self.base_url)

    def excption_handler(self, exception_class, error, error_msg):
        try:
            raise exception_class(error, error_msg)
        except exception_class as e:
            print(str(e))
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
            except ValueError as e:
                if content.strip() == "":
                    return rst
                if res.get('content-type') and res['content-type'] not in media_types:
                    print("\n\tInvalid media type %s in REST response.\n\tPlease check that the server URL is correct, "
                          "including the protocol (http/https).\n\tIf the URL is correct, "
                          "there may be a configuration problem on the server.\n" % res['content-type'])
                    sys.exit(1)
                else:
                    print("Exception while decoding: %s" % e)
            return rst
        elif res['status'] == '201':
            return True
        elif res['status'] in EXCEPTION_STATUS_DICT:
            self.excption_handler(*EXCEPTION_STATUS_DICT[res['status']])
        else:
            self.excption_handler(UnexpectedStatusException,
                                  'Error', 'Unexpected Status (%s), failed to push: %s' % (res['status'], extra_msg or ""))

    def _to_unicode(self, some_string):
        if not isinstance(some_string, str):
            return str(some_string)
        return some_string
