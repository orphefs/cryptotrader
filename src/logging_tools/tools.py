import wrapt
import logging as logger

@wrapt.decorator
def print_function_context(wrapped, instance, args, kwargs):
    if instance:
        name = instance.__name__
    else:
        name = None
    logger.info("===> Entering method {}.{}".format(name, wrapped.__name__))
    result = wrapped(*args, **kwargs)
    logger.info("Exiting method {}.{} ===> ".format(name, wrapped.__name__))
    return result