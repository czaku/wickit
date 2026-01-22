"""presets - AI Configuration Presets.

Pre-configured settings for popular AI providers and use cases.
Provides ready-to-use configurations for common AI setups.

Example:
    >>> from wickit import presets
    >>> ollama = presets.OLLAMA_DEFAULT
    >>> claude = presets.CLAUDE_SONNET
    >>> config = presets.apply_preset("OLLAMA_DEFAULT")
    >>> all_presets = presets.list_presets()

Classes:
    AIPreset: Preset configuration with name, engine, model, temperature, etc.

Built-in Presets:
    OLLAMA_DEFAULT - Llama 3.2 with defaults
    OLLAMA_CODING - Optimized for code generation
    CLAUDE_SONNET - Claude 4 Sonnet balanced
    CLAUDE_OPUS - Claude 4 Opus powerful
    GPT4_BALANCED - GPT-4 balanced performance
    GPT4_FAST - GPT-4 fast/ Turbo
    OPENAI_DEFAULT - GPT-3.5/4 defaults

Functions:
    get_preset: Get preset by name.
    apply_preset: Apply preset to Config.
    list_presets: List all preset names.
"""

from dataclasses import dataclass
from typing import Optional

from .knobs import AIConfig


@dataclass
class AIPreset:
    """Pre-configured AI settings."""
    name: str
    description: str
    engine: str
    model: str
    timeout: int = 300
    retry_count: int = 3
    retry_delay: int = 5

    def to_ai_config(self) -> AIConfig:
        """Convert to AIConfig."""
        return AIConfig(
            engine=self.engine,
            model=self.model,
            timeout=self.timeout,
            retry_count=self.retry_count,
            retry_delay=self.retry_delay,
        )


# Preset definitions
OLLAMA_DEFAULT = AIPreset(
    name="ollama_default",
    description="Balanced Ollama settings for general use",
    engine="ollama",
    model="llama3.2",
    timeout=300,
    retry_count=3,
    retry_delay=5,
)

OLLAMA_CODING = AIPreset(
    name="ollama_coding",
    description="Optimized for code generation",
    engine="ollama",
    model="codellama",
    timeout=600,
    retry_count=3,
    retry_delay=10,
)

CLAUDE_SONNET = AIPreset(
    name="claude_sonnet",
    description="Claude 3.5 Sonnet - balanced performance",
    engine="claude",
    model="claude-3-5-sonnet-20241022",
    timeout=600,
    retry_count=3,
    retry_delay=5,
)

CLAUDE_OPUS = AIPreset(
    name="claude_opus",
    description="Claude 3 Opus - for complex reasoning",
    engine="claude",
    model="claude-3-opus-20240229",
    timeout=900,
    retry_count=5,
    retry_delay=10,
)

GPT4_BALANCED = AIPreset(
    name="gpt4_balanced",
    description="GPT-4 balanced performance",
    engine="openai",
    model="gpt-4",
    timeout=600,
    retry_count=3,
    retry_delay=5,
)

GPT4_FAST = AIPreset(
    name="gpt4_fast",
    description="GPT-4 for quick responses",
    engine="openai",
    model="gpt-4-turbo",
    timeout=300,
    retry_count=2,
    retry_delay=3,
)

OPENAI_DEFAULT = AIPreset(
    name="openai_default",
    description="Standard OpenAI settings",
    engine="openai",
    model="gpt-4o",
    timeout=600,
    retry_count=3,
    retry_delay=5,
)

# All presets registry
PRESETS = {
    "ollama_default": OLLAMA_DEFAULT,
    "ollama_coding": OLLAMA_CODING,
    "claude_sonnet": CLAUDE_SONNET,
    "claude_opus": CLAUDE_OPUS,
    "gpt4_balanced": GPT4_BALANCED,
    "gpt4_fast": GPT4_FAST,
    "openai_default": OPENAI_DEFAULT,
}


def get_preset(name: str) -> Optional[AIPreset]:
    """Get a preset by name.

    Args:
        name: Preset name (e.g., "ollama_default", "claude_sonnet")

    Returns:
        AIPreset if found, None otherwise
    """
    return PRESETS.get(name)


def apply_preset(product_name: str, preset_name: str) -> bool:
    """Apply a preset to a product's config.

    Args:
        product_name: Product name (e.g., "jobforge", "studya")
        preset_name: Preset name (e.g., "ollama_default")

    Returns:
        True if applied, False if preset not found
    """
    from .knobs import get_config, save_config

    preset = get_preset(preset_name)
    if not preset:
        return False

    config = get_config(product_name)
    config.ai = preset.to_ai_config()
    save_config(product_name, config)
    return True


def list_presets() -> list:
    """List all available presets.

    Returns:
        List of preset info dicts
    """
    return [
        {
            "name": p.name,
            "description": p.description,
            "engine": p.engine,
            "model": p.model,
        }
        for p in PRESETS.values()
    ]


def list_presets_by_engine(engine: str) -> list:
    """List presets for a specific engine.

    Args:
        engine: Engine name (e.g., "ollama", "claude", "openai")

    Returns:
        List of preset info dicts
    """
    return [
        {
            "name": p.name,
            "description": p.description,
            "model": p.model,
        }
        for p in PRESETS.values()
        if p.engine == engine
    ]
