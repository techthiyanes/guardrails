from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional

from opentelemetry.trace import Span

from guardrails.types.primitives import PrimitiveTypes
from guardrails.utils.safe_get import safe_get
from guardrails.utils.hub_telemetry_utils import HubTelemetry


def get_guard_call_attributes(
    attrs: Dict[str, Any], origin: str, *args, **kwargs
) -> Dict[str, Any]:
    attrs["stream"] = kwargs.get("stream", False)

    guard_self = safe_get(args, 0)
    if guard_self is not None:
        attrs["guard_id"] = guard_self.id
        attrs["user_id"] = guard_self._user_id
        attrs["custom_reask_prompt"] = guard_self._exec_opts.reask_prompt is not None
        attrs["custom_reask_instructions"] = (
            guard_self._exec_opts.reask_instructions is not None
        )
        attrs["custom_reask_messages"] = (
            guard_self._exec_opts.reask_messages is not None
        )
        attrs["output_type"] = (
            "unstructured"
            if PrimitiveTypes.is_primitive(
                guard_self.output_schema.type.actual_instance
            )
            else "structured"
        )
        return attrs

    llm_api_str = ""  # noqa
    llm_api = kwargs.get("llm_api")
    if origin in ["Guard.__call__", "AsyncGuard.__call__"]:
        llm_api = safe_get(args, 1, llm_api)

    if llm_api:
        llm_api_module_name = (
            llm_api.__module__ if hasattr(llm_api, "__module__") else ""
        )
        llm_api_name = (
            llm_api.__name__ if hasattr(llm_api, "__name__") else type(llm_api).__name__
        )
        llm_api_str = f"{llm_api_module_name}.{llm_api_name}"
    attrs["llm_api"] = llm_api_str if llm_api_str else "None"

    return attrs


def add_attributes(
    span: Span, attrs: Dict[str, Any], name: str, origin: str, *args, **kwargs
):
    attrs["origin"] = origin
    if name == "/guard_call":
        attrs = get_guard_call_attributes(attrs, *args, **kwargs)

    for key, value in attrs.items():
        span.set_attribute(key, value)


def trace(
    *,
    name: str,
    origin: str,
    is_parent: Optional[bool] = False,
    **attrs,
):
    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            hub_telemetry = HubTelemetry()
            if hub_telemetry._enabled and hub_telemetry._tracer is not None:
                context = (
                    hub_telemetry.extract_current_context() if not is_parent else None
                )
                with hub_telemetry._tracer.start_as_current_span(
                    name, context=context
                ) as span:  # noqa
                    if is_parent:
                        # Inject the current context
                        hub_telemetry.inject_current_context()

                    add_attributes(span, attrs, origin, *args, **kwargs)
                    return fn(*args, **kwargs)
            else:
                return fn(*args, **kwargs)

        return wrapper

    return decorator


def async_trace(
    *,
    name: str,
    origin: str,
    is_parent: Optional[bool] = False,
):
    def decorator(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            hub_telemetry = HubTelemetry()
            if hub_telemetry._enabled and hub_telemetry._tracer is not None:
                context = (
                    hub_telemetry.extract_current_context() if not is_parent else None
                )
                with hub_telemetry._tracer.start_as_current_span(
                    name, context=context
                ) as span:  # noqa
                    if is_parent:
                        # Inject the current context
                        hub_telemetry.inject_current_context()
                    add_attributes(span, {"async": True}, origin, *args, **kwargs)
                    return await fn(*args, **kwargs)
            else:
                return await fn(*args, **kwargs)

        return async_wrapper

    return decorator
