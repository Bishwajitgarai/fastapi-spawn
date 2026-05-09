"""Tests for fastapi_spawn.validators."""

import pytest

from fastapi_spawn.constants import ORM, Database
from fastapi_spawn.validators import validate_orm_db_compat, validate_project_name


class TestValidateProjectName:
    def test_valid_simple(self):
        assert validate_project_name("my-api") == "my-api"

    def test_valid_underscore(self):
        assert validate_project_name("my_project") == "my_project"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            validate_project_name("")

    def test_starts_with_digit_raises(self):
        with pytest.raises(ValueError, match="Invalid project name"):
            validate_project_name("1project")

    def test_special_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid project name"):
            validate_project_name("my project!")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="64 characters"):
            validate_project_name("a" * 65)


class TestOrmDbCompat:
    def test_sqlalchemy_postgres_ok(self):
        validate_orm_db_compat(ORM.sqlalchemy, Database.postgresql)

    def test_beanie_mongo_ok(self):
        validate_orm_db_compat(ORM.beanie, Database.mongodb)

    def test_beanie_postgres_raises(self):
        with pytest.raises(ValueError, match="not compatible"):
            validate_orm_db_compat(ORM.beanie, Database.postgresql)

    def test_sqlalchemy_mongo_raises(self):
        with pytest.raises(ValueError, match="not compatible"):
            validate_orm_db_compat(ORM.sqlalchemy, Database.mongodb)

    def test_none_orm_any_db_ok(self):
        for db in Database:
            validate_orm_db_compat(ORM.none, db)
