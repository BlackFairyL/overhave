from typing import cast
from uuid import uuid1

import allure
import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker
from pydantic import SecretStr

from overhave import db
from overhave.storage import (
    FeatureModel,
    FeatureTypeModel,
    ScenarioModel,
    ScenarioStorage,
    SystemUserGroupStorage,
    SystemUserModel,
    SystemUserStorage,
    TagModel,
    TestRunStorage,
    TestUserModel,
    TestUserSpecification,
    TestUserStorage,
)


@pytest.fixture(scope="package")
def test_system_user_storage() -> SystemUserStorage:
    return SystemUserStorage()


@pytest.fixture(scope="package")
def test_system_user_group_storage() -> SystemUserGroupStorage:
    return SystemUserGroupStorage()


@pytest.fixture(scope="package")
def test_user_storage() -> TestUserStorage:
    return TestUserStorage()


@pytest.fixture()
def test_feature_type(database: None, faker: Faker) -> FeatureTypeModel:
    with db.create_session() as session:
        feature_type = db.FeatureType(name=cast(str, faker.word()))
        session.add(feature_type)
        session.flush()
        return cast(FeatureTypeModel, FeatureTypeModel.from_orm(feature_type))


@pytest.fixture()
def test_user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_system_user(
    test_system_user_storage: SystemUserStorage, database: None, faker: Faker, test_user_role: db.Role
) -> SystemUserModel:
    return test_system_user_storage.create_user(
        login=faker.word(), password=SecretStr(faker.word()), role=test_user_role
    )


@pytest.fixture()
def test_specification() -> TestUserSpecification:
    return TestUserSpecification({"test": "value"})


@pytest.fixture()
def test_testuser(
    test_system_user: SystemUserModel, faker: Faker, test_feature_type, test_specification: TestUserSpecification
) -> TestUserModel:
    with db.create_session() as session:
        test_user = db.TestUser(
            feature_type_id=test_feature_type.id,
            name=cast(str, faker.word()),
            created_by=test_system_user.login,
            specification=test_specification,
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_tag(test_system_user: SystemUserModel, faker: Faker) -> TagModel:
    with db.create_session() as session:
        tag = db.Tags(value=faker.word(), created_by=test_system_user.login)
        session.add(tag)
        session.flush()
        return cast(TagModel, TagModel.from_orm(tag))


@pytest.fixture()
def test_severity(request: FixtureRequest) -> allure.severity_level:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_feature(
    test_system_user: SystemUserModel,
    test_feature_type: FeatureTypeModel,
    test_severity: allure.severity_level,
    faker: Faker,
) -> FeatureModel:
    with db.create_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=test_system_user.login,
            type_id=test_feature_type.id,
            task=[faker.word()[:11]],
            file_path=f"{faker.word()}/{faker.word()}",
            severity=test_severity,
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_feature_with_tag(test_feature: FeatureModel, test_tag: TagModel) -> FeatureModel:
    with db.create_session() as session:
        tag = session.query(db.Tags).filter(db.Tags.id == test_tag.id).one()
        feature = session.query(db.Feature).filter(db.Feature.id == test_feature.id).one()
        feature.feature_tags.append(tag)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_scenario_storage() -> ScenarioStorage:
    return ScenarioStorage()


@pytest.fixture(scope="class")
def test_run_storage() -> TestRunStorage:
    return TestRunStorage()


@pytest.fixture()
def test_created_test_run_id(
    test_run_storage: TestRunStorage, test_scenario: ScenarioModel, test_feature: FeatureModel
) -> int:
    return test_run_storage.create_test_run(test_scenario.id, test_feature.author)


@pytest.fixture()
def test_scenario(test_feature: FeatureModel, faker: Faker) -> ScenarioModel:
    with db.create_session() as session:
        db_scenario = db.Scenario(feature_id=test_feature.id, text=faker.word())
        session.add(db_scenario)
        session.flush()
        return cast(ScenarioModel, ScenarioModel.from_orm(db_scenario))


@pytest.fixture(scope="class")
def test_report() -> str:
    return uuid1().hex
