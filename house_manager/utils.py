import sentry_sdk  # type:ignore

def report_exception(func):
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
    return f
