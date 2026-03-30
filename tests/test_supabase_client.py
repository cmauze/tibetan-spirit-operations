"""Tests for the Supabase client wrapper."""

import os
import sys
from unittest.mock import patch

import pytest


def _get_real_get_client():
    """Return the real get_client function, bypassing any sys.modules mocks."""
    # test_server.py injects a MagicMock for ts_shared.supabase_client at module
    # level with no cleanup. Remove the mock so we test the real implementation.
    for mod in ("ts_shared.supabase_client", "ts_shared"):
        if mod in sys.modules and hasattr(sys.modules[mod], "_mock_name"):
            del sys.modules[mod]
    from ts_shared.supabase_client import get_client
    return get_client


def test_get_client_missing_url():
    """get_client raises EnvironmentError when SUPABASE_URL is missing."""
    get_client = _get_real_get_client()
    get_client.cache_clear()

    with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_SERVICE_KEY": "test"}):
        with pytest.raises(EnvironmentError, match="SUPABASE_URL"):
            get_client()


def test_get_client_missing_key():
    """get_client raises EnvironmentError when SUPABASE_SERVICE_KEY is missing."""
    get_client = _get_real_get_client()
    get_client.cache_clear()

    with patch.dict(os.environ, {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_KEY": ""}):
        with pytest.raises(EnvironmentError, match="SUPABASE_SERVICE_KEY"):
            get_client()
