"""
Materialized view refresher for Supabase.

Requires a PostgreSQL function in Supabase:
    CREATE OR REPLACE FUNCTION refresh_materialized_view(view_name text)
    RETURNS void AS $$
    BEGIN
      EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', view_name);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;

This function will be created in the Sprint S1 Phase 1D migration.

Usage:
    from ts_shared.views import refresh_views

    refresh_views(["channel_profitability_monthly", "product_margin_detail"])
"""

import logging

logger = logging.getLogger(__name__)

KNOWN_VIEWS = [
    "channel_profitability_monthly",
    "product_margin_detail",
    "inventory_health",
    "marketing_roas_trailing",
]


def refresh_views(view_names: list[str]) -> dict[str, bool]:
    """Refresh one or more materialized views via Supabase RPC.

    Args:
        view_names: List of materialized view names to refresh.

    Returns:
        Dict of view_name -> success (True/False).
    """
    results: dict[str, bool] = {}
    client = None

    for name in view_names:
        if name not in KNOWN_VIEWS:
            logger.warning("Unknown materialized view: %s (skipping)", name)
            results[name] = False
            continue
        try:
            if client is None:
                from ts_shared.supabase_client import get_client
                client = get_client()
            client.rpc("refresh_materialized_view", {"view_name": name}).execute()
            logger.info("Refreshed materialized view: %s", name)
            results[name] = True
        except Exception as e:
            logger.error("Failed to refresh view %s: %s", name, e)
            results[name] = False

    return results
