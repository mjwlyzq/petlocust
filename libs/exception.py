from requests import Response


class LocustException(Exception):
    def __init__(self, msg=''):
        super().__init__()
        self.msg = f"{self.__class__.__name__}: {msg}"

    def __str__(self):
        return str(self.msg)

    def __repr__(self):
        return str(self.msg)


class ResponseException(LocustException):
    def __init__(self, rep: Response):
        super().__init__(
            f"{rep.status_code} {rep.json() if rep.status_code == 200 else rep.text} url: {rep.request.url}")


class AccountInvalidException(LocustException):
    def __init__(self, rep: Response):
        super().__init__(f"Code-{rep.status_code}: {rep.json()}")


class RequestWasAbortedException(LocustException):
    def __init__(self, rep: Response):
        super().__init__(
            f"{rep.status_code} {rep.json() if rep.status_code == 200 else rep.text} url: {rep.request.url}")


class IotException(LocustException):
    pass


class FitureException(LocustException):
    def __init__(self, msg=''):
        super(FitureException, self).__init__(f"业务报错: {msg}")
