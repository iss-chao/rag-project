from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from schemas.response import ApiResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            code=exc.status_code,
            msg=exc.detail,
            data=None
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.body 拿到前端原始请求体
    # exc.errors() detail数组
    print(exc.errors())

    # 自定义返回格式，替换默认的报错json
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            code=40001,
            msg="请求参数格式错误",
            data=None
        ).model_dump()
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    err_msg = str(exc.orig)
    print("数据库约束错误：", err_msg)
    print("数据库约束错误：", err_msg)
    if "1452" in err_msg:
        msg = "关联数据不存在，外键校验失败"
    elif "1451" in err_msg:
        # 就是你现在删除时报的
        msg = "该数据有关联子数据，无法删除，请先删除关联数据"
    elif "1062" in err_msg:
        msg = "数据重复，唯一索引冲突"
    else:
        msg = "数据库保存失败，违反数据约束"
    return JSONResponse(
        status_code=400,
        content=ApiResponse(
            code=400,
            msg=msg,
            data=None
        ).model_dump()
    )