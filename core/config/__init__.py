"""Compatibility shim for core.config package.

Canonical implementations live in distill_lib.core.config.* modules.
"""

from distill_lib.core.config.loader import (
    ConfigValidationError,
    get_api_key_env_var,
    get_api_key_for_provider,
    get_base_url_for_provider,
    get_config,
    get_config_path,
    get_model_config,
    is_api_key_configured,
    load_config,
    reload_config,
    validate_config,
)
from distill_lib.core.config.utils import (
    create_default_config,
    get_config_summary,
    validate_config_file_exists,
    write_config,
)

__all__ = [
    "get_config",
    "load_config",
    "reload_config",
    "get_model_config",
    "ConfigValidationError",
    "get_config_path",
    "validate_config",
    "get_api_key_env_var",
    "get_api_key_for_provider",
    "is_api_key_configured",
    "get_base_url_for_provider",
    "validate_config_file_exists",
    "get_config_summary",
    "create_default_config",
    "write_config",
]
