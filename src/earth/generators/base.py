"""
Base generator infrastructure for Earth data generation.

Provides a consistent interface and common functionality for all entity generators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic, cast
from dataclasses import dataclass
import random
from faker import Faker

# Generic type for profile objects
T = TypeVar("T")


@dataclass
class GeneratorConfig:
    """Configuration for data generators."""

    locale: str = "en_US"
    seed: Optional[int] = None
    batch_size: int = 1000

    def __post_init__(self) -> None:
        """Initialize random seeds if provided."""
        if self.seed is not None:
            Faker.seed(self.seed)
            random.seed(self.seed)


class BaseGenerator(ABC, Generic[T]):
    """
    Abstract base class for all entity generators.

    Provides common functionality and enforces consistent interface.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize generator with configuration.

        Args:
            config: Generator configuration (uses defaults if None)
        """
        self.config = config or GeneratorConfig()
        self.fake = Faker(self.config.locale)

        # Apply seed if provided
        if self.config.seed is not None:
            Faker.seed(self.config.seed)
            random.seed(self.config.seed)

    @property
    @abstractmethod
    def entity_name(self) -> str:
        """Return the name of the entity this generator creates."""
        pass

    @property
    @abstractmethod
    def required_fields(self) -> List[str]:
        """Return list of required fields for validation."""
        pass

    @abstractmethod
    def generate_profile(self) -> T:
        """
        Generate a single entity profile.

        Returns:
            Profile object of type T
        """
        pass

    def generate_batch(self, count: int) -> List[T]:
        """
        Generate multiple entity profiles.

        Args:
            count: Number of profiles to generate

        Returns:
            List of profile objects
        """
        return [self.generate_profile() for _ in range(count)]

    def generate_batch_dicts(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate multiple entity profiles as dictionaries.

        Args:
            count: Number of profiles to generate

        Returns:
            List of profile dictionaries ready for database storage
        """
        profiles = self.generate_batch(count)
        return [self._profile_to_dict(profile) for profile in profiles]

    def _profile_to_dict(self, profile: T) -> Dict[str, Any]:
        """
        Convert profile object to dictionary.

        Args:
            profile: Profile object to convert

        Returns:
            Dictionary representation
        """
        if hasattr(profile, "to_dict"):
            return cast(dict, profile.to_dict())
        elif hasattr(profile, "__dict__"):
            # Fallback for objects with __dict__
            return self._sanitize_dict(profile.__dict__)
        else:
            raise NotImplementedError(
                f"Profile type {type(profile)} must implement to_dict() method"
            )

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize dictionary for database storage.

        Args:
            data: Raw dictionary data

        Returns:
            Sanitized dictionary
        """
        from datetime import date, datetime

        result = {}
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    def validate_profile(self, profile: T) -> bool:
        """
        Validate a generated profile.

        Args:
            profile: Profile to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            profile_dict = self._profile_to_dict(profile)
            # Check required fields exist and are not None
            for field in self.required_fields:
                if field not in profile_dict or profile_dict[field] is None:
                    if profile_dict[field] is None:
                        print(f"{field} does not exist for {profile}")
                    elif field not in profile_dict:
                        print(f"Required field: {field} not found for {profile}")
                    return False
                print(f"Validated {field}")
            # Additional custom validation
            return self._custom_validation(profile_dict)

        except Exception:
            return False

    def _custom_validation(self, profile_dict: Dict[str, Any]) -> bool:
        """
        Override this method for entity-specific validation logic.

        Args:
            profile_dict: Profile dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        return True

    def validate_batch(self, profiles: List[T]) -> bool:
        """
        Validate a batch of profiles.

        Args:
            profiles: List of profiles to validate

        Returns:
            True if all profiles are valid, False otherwise
        """
        return all(self.validate_profile(profile) for profile in profiles)

    def get_generation_stats(self, profiles: List[T]) -> Dict[str, Any]:
        """
        Get statistics about generated profiles.

        Args:
            profiles: List of generated profiles

        Returns:
            Dictionary with generation statistics
        """
        if not profiles:
            return {"count": 0, "entity_type": self.entity_name}

        stats = {
            "count": len(profiles),
            "entity_type": self.entity_name,
            "config": {
                "locale": self.config.locale,
                "seed": self.config.seed,
            },
        }

        # Add custom stats
        custom_stats = self._get_custom_stats(profiles)
        stats.update(custom_stats)

        return stats

    def _get_custom_stats(self, profiles: List[T]) -> Dict[str, Any]:
        """
        Override this method for entity-specific statistics.

        Args:
            profiles: List of generated profiles

        Returns:
            Dictionary with custom statistics
        """
        return {}

    def reset_seed(self, seed: Optional[int] = None) -> None:
        """
        Reset the random seed for this generator.

        Args:
            seed: New seed value (uses current config seed if None)
        """
        if seed is not None:
            self.config.seed = seed

        if self.config.seed is not None:
            Faker.seed(self.config.seed)
            random.seed(self.config.seed)
