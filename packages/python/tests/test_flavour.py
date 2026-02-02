"""
Tests for wickit.flavour module - Environment management
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from wickit.flavour import (
    Environment,
    EnvironmentType,
    get_environment,
    register_environment,
    is_production,
    is_development,
    is_local,
)


class TestEnvironment:
    """Test Environment class."""
    
    def test_environment_creation(self):
        """Test creating an environment."""
        env = Environment(name="test", type=EnvironmentType.DEVELOPMENT)
        assert env.name == "test"
        assert env.type == EnvironmentType.DEVELOPMENT
        assert env.is_development is True
        assert env.is_production is False
    
    def test_production_environment(self):
        """Test production environment flags."""
        env = Environment(name="production", type=EnvironmentType.PRODUCTION)
        assert env.is_production is True
        assert env.is_development is False
        assert env.is_local is False
    
    def test_local_environment(self):
        """Test local environment flags."""
        env = Environment(name="local", type=EnvironmentType.LOCAL)
        assert env.is_local is True
        assert env.is_production is False
    
    def test_to_shuffle_context(self):
        """Test conversion to shuffle context."""
        env = Environment(
            name="development",
            type=EnvironmentType.DEVELOPMENT
        )
        context = env.to_shuffle_context()
        assert context["environment"] == "development"
        assert context["type"] == "development"
        assert context["is_development"] is True


class TestGetEnvironment:
    """Test environment detection."""
    
    def test_explicit_name(self):
        """Test getting environment by explicit name."""
        env = get_environment("production")
        assert env.name == "production"
        assert env.is_production is True
    
    def test_from_env_var(self):
        """Test detection from WICKIT_ENV environment variable."""
        with patch.dict(os.environ, {"WICKIT_ENV": "staging"}):
            env = get_environment()
            assert env.name == "staging"
    
    def test_from_git_branch_main(self):
        """Test detection from git branch 'main'."""
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_result.returncode = 0
        
        with patch("subprocess.run", return_value=mock_result):
            with patch.dict(os.environ, {}, clear=True):
                env = get_environment()
                assert env.name == "production"
    
    def test_from_git_branch_develop(self):
        """Test detection from git branch 'develop'."""
        mock_result = MagicMock()
        mock_result.stdout = "develop\n"
        mock_result.returncode = 0
        
        with patch("subprocess.run", return_value=mock_result):
            with patch.dict(os.environ, {}, clear=True):
                env = get_environment()
                assert env.name == "development"
    
    def test_from_hostname_local(self):
        """Test detection from localhost hostname."""
        with patch("socket.gethostname", return_value="localhost"):
            with patch.dict(os.environ, {}, clear=True):
                with patch("subprocess.run", side_effect=Exception("no git")):
                    env = get_environment()
                    assert env.name == "local"
    
    def test_default_to_local(self):
        """Test default fallback to local."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("socket.gethostname", return_value="unknown"):
                with patch("subprocess.run", side_effect=Exception("no git")):
                    env = get_environment()
                    assert env.name == "local"


class TestRegisterEnvironment:
    """Test custom environment registration."""
    
    def test_register_custom_environment(self):
        """Test registering a custom environment."""
        parent = get_environment("development")
        env = register_environment(
            "qa",
            parent=parent,
            config_overrides={"database": {"name": "qa_db"}}
        )
        
        assert env.name == "qa"
        assert env.type == EnvironmentType.CUSTOM
        assert env.parent == parent
    
    def test_custom_environment_retrieval(self):
        """Test retrieving a registered custom environment."""
        register_environment("preview", config_overrides={})
        env = get_environment("preview")
        assert env.name == "preview"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_is_production(self):
        """Test is_production() function."""
        with patch("wickit.flavour.get_environment") as mock_get:
            mock_get.return_value = Environment(
                name="production",
                type=EnvironmentType.PRODUCTION
            )
            assert is_production() is True
    
    def test_is_development(self):
        """Test is_development() function."""
        with patch("wickit.flavour.get_environment") as mock_get:
            mock_get.return_value = Environment(
                name="development",
                type=EnvironmentType.DEVELOPMENT
            )
            assert is_development() is True
    
    def test_is_local(self):
        """Test is_local() function."""
        with patch("wickit.flavour.get_environment") as mock_get:
            mock_get.return_value = Environment(
                name="local",
                type=EnvironmentType.LOCAL
            )
            assert is_local() is True


class TestEnvironmentConfig:
    """Test environment configuration."""
    
    def test_get_config_with_parent(self):
        """Test config inheritance from parent."""
        parent = Environment(
            name="development",
            type=EnvironmentType.DEVELOPMENT,
            config_overrides={"shared_key": "parent_value"}
        )
        
        child = register_environment(
            "feature-branch",
            parent=parent,
            config_overrides={"child_key": "child_value"}
        )
        
        # Child should have both parent and child configs
        assert "shared_key" in child.config_overrides or child.parent.config_overrides
        assert "child_key" in child.config_overrides


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
