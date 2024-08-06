from locust import events


class EventReport(object):
    @staticmethod
    def success(request_type: str = "MQTT",
                name: str = "Default",
                response_time: int = 0,
                response_length: int = 0):
        events.request.fire(request_type=request_type,
                            name=name,
                            response_time=response_time,
                            response_length=response_length, )

    @staticmethod
    def failure(request_type: str = "MQTT",
                name: str = "Default",
                response_time: int = 0,
                response_length: int = 0,
                exception: Exception = None):
        events.request.fire(request_type=request_type,
                            name=name,
                            response_time=response_time,
                            response_length=response_length,
                            exception=exception)
