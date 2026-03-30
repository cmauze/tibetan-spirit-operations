"""Tests for the Supabase client wrapper."""

import os
from unittest.mock import patch

import pytest

from ts_shared.supabase_client import get_client


def test_get_client_missing_url():
    """get_client raises EnvironmentError when SUPABASE_URL is missing."""
    get_client.cache_clear()

    with patch.dict(os.environ, {"SUPABASE_URL": "", "SUPABASE_SERVICE_KEY": "test"}):
        with pytest.raises(EnvironmentError, match="SUPABASE_URL"):
            get_client()


def test_get_client_missing_key():
    """get_client raises EnvironmentError when SUPABASE_SERVICE_KEY is missing."""
    get_client.cache_clear()

    with patch.dict(os.environ, {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_KEY": ""}):
        with pytest.raises(EnvironmentError, match="SUPABASE_SERVICE_KEY"):
            get_client()
