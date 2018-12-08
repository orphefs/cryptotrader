import wrapt
import logging as logger


@wrapt.decorator
def print_context(wrapped, instance, args, kwargs):
    logger.info("===> Entering method {}.{}".format(instance.__name__, wrapped.__name__))
    result = wrapped(*args, **kwargs)
    logger.info("Exiting method {}.{} ===> ".format(instance.__name__, wrapped.__name__))
    return result
