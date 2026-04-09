# core/api.py - Core Combat System API
"""
Unified API for the core combat system.
All external modules should import from this file.
"""

# Combat Engine (main entry point)
from .modules.combat import process_attack

# Stamina System (external interface)
from .modules.stamina import get_initial_stamina, apply_stamina

# Fatigue System (telemetry interface)
from .modules.fatigue import get_stamina_level, FATIGUE_LEVEL_FRESH, FATIGUE_LEVEL_TIRED, FATIGUE_LEVEL_EXHAUSTED

# EHP Calculations
from .modules.ehp import EHPDamageCalculator

# Configuration (read-only access)
from copy import deepcopy
from .config import CONFIG as _CONFIG

CORE_VERSION = "15.7"

def get_config():
    """Get read-only copy of configuration to prevent runtime mutations"""
    return deepcopy(_CONFIG)

__all__ = [
    # === CORE COMBAT ===
    'process_attack',        # Main combat function

    # === STAMINA SYSTEM ===
    'get_initial_stamina',   # Fighter creation
    'apply_stamina',         # Stamina updates

    # === TELEMETRY ===
    'get_stamina_level',     # Fatigue states
    'FATIGUE_LEVEL_FRESH',   # State constants
    'FATIGUE_LEVEL_TIRED',
    'FATIGUE_LEVEL_EXHAUSTED',

    # === CONFIGURATION ===
    'get_config',            # Read-only config access

    # === VERSIONING ===
    'CORE_VERSION'           # Version tracking for compatibility
]