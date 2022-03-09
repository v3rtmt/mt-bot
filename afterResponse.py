from werkzeug.wsgi import ClosingIterator
from traceback import print_exc

class AfterResponse:
    def __init__(self, application=None):
        self.functions = list()
        if application:
            self.init_app(application)    

    def __call__(self, function):
        self.functions.append(function)

    def init_app(self, application):
        application.after_response = self
        application.wsgi_app = AfterResponseMiddleware(application.wsgi_app, self)

    def flush(self):
        while self.functions:
            try:
                self.functions.pop()()
            except Exception:
                print_exc()


class AfterResponseMiddleware:
    def __init__(self, application, after_response_ext):
        self.application = application
        self.after_response_ext = after_response_ext

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.after_response_ext.flush])
        except Exception:
            print_exc()
            return iterator
