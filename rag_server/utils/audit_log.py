from functools import wraps


def audit_log(resource_type: str): # 接收你注解传的参数
    def decorator(func):                 # 接收被装饰的函数本身
        @wraps(func)
        async def wrapper(*args, **kwargs): # 真正替换原函数，拦截参数、执行逻辑
            # 在这里写前置/后置逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator
