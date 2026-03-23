"""
Supabase client wrapper for the Tibetan Spirit operations database.

Usage:
    from ts_shared.supabase_client import get_client

    client = get_client()
    result = client.table("products").select("*").eq("status", "active").execute()
"""

import os
from functools import lru_cache

# from supabase import create_client, Client


@lru_cache(maxsize=1)
def get_client():
    """
    Get a singleton Supabase client using service key (bypasses RLS).

    Returns the client configured for the operations database.
    Requires SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set. "
            "See server/.env.example for required environment variables."
        )

    # TODO: Uncomment when supabase package is installed
    # return create_client(url, key)
    raise NotImplementedError("Supabase client not yet configured — provision database first")
