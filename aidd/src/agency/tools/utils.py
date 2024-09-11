from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Annotated, get_origin

from autogen import ConversableAgent
from langchain.tools import BaseTool
from settings import settings


class AccessDeniedError(Exception):
    pass


def validate_path(path: str | None = None):
    if path is None:
        path = "."

    if Path(path).is_absolute():
        raise AccessDeniedError(f"Access denied: Absolute path {path} is not allowed.")

    full_path = (settings.project_dir / path).resolve()
    if not full_path.is_relative_to(settings.project_dir):
        raise AccessDeniedError(f"Access denied: Attempted access outside of project directory at path: {path}")

    return full_path


def generate_tool_schema(tool: BaseTool) -> dict[str, dict]:
    """Generate the OpenAI schema for the tool."""
    schema = tool.tool_call_schema.schema()

    # ! FIX: double assignment of title and description
    schema.pop("title", None)
    schema.pop("description", None)

    name = tool.name.lower().replace(" ", "_")

    return name, {
        "type": "function",
        "function": {
            "name": name,
            "description": tool.description,
            "parameters": schema,
        },
    }


def register_langchain_tool(
    tool: BaseTool,
    caller: ConversableAgent,
    executor: ConversableAgent,
):
    """Register the tool with the caller and executor."""
    name, tool_sig = generate_tool_schema(tool)
    caller.update_tool_signature(tool_sig, is_remove=False)
    executor.register_function({name: tool._run})


# def valid_path(_func=None, *, path_args: list[str] = ["path"]):
#     """Decorator to validate the path.
#     CAUTION: Rewrites the path annotations to str."""

#     def decorator(func: Callable):
#         arg_names = func.__code__.co_varnames

#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             args = list(args)
#             pos_args = [arg for arg in arg_names if arg not in kwargs]
#             try:
#                 for arg in path_args:
#                     if arg in kwargs:
#                         kwargs[arg] = validate_path(kwargs[arg])
#                     else:
#                         idx = pos_args.index(arg)
#                         args[idx] = validate_path(args[idx])

#             except AccessDeniedError as e:
#                 return str(e) + "\nTry again with a valid path."

#             return func(*args, **kwargs)

#         for arg in path_args:
#             annotation = wrapper.__annotations__[arg]
#             if get_origin(annotation) is Annotated:
#                 new_annotation = Annotated[str, ""]
#                 new_annotation.__metadata__ = annotation.__metadata__
#             else:
#                 new_annotation = str

#             wrapper.__annotations__[arg] = new_annotation

#         return wrapper

#     if _func is not None:
#         return decorator(_func)

#     return decorator
