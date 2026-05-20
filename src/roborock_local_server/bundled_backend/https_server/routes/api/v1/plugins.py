from __future__ import annotations

from typing import Any

from shared.context import ServerContext

from ...auth.service import ok
from ...plugin.common import CATEGORY_PLUGIN_LIST, plugin_records_with_snapshot_fallback, proxied_plugin_records


def match(path: str) -> bool:
    clean = path.rstrip("/")
    return clean in {"/api/v1/plugins", "api/v1/plugins"}


def build(
    ctx: ServerContext,
    _query_params: dict[str, list[str]],
    _body_params: dict[str, list[str]],
    _clean_path: str,
) -> dict[str, Any]:
    records = plugin_records_with_snapshot_fallback(
        ctx,
        "plugins",
        CATEGORY_PLUGIN_LIST,
        list_key="categoryPluginList",
    )
    return ok({"categoryPluginList": proxied_plugin_records(ctx, records)})

