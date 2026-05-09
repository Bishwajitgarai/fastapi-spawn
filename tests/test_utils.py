"""Tests for fastapi_spawn.utils."""

from fastapi_spawn.utils import to_kebab_case, to_pascal_case, to_snake_case


class TestCaseConversions:
    def test_snake_case(self):
        assert to_snake_case("MyProject") == "my_project"
        assert to_snake_case("my-project") == "my_project"
        assert to_snake_case("my project") == "my_project"

    def test_pascal_case(self):
        assert to_pascal_case("my_project") == "MyProject"
        assert to_pascal_case("my-project") == "MyProject"

    def test_kebab_case(self):
        assert to_kebab_case("my_project") == "my-project"
        assert to_kebab_case("MyProject") == "my-project"
