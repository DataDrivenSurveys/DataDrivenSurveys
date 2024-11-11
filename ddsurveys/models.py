"""This module defines the database models and utility functions for the project.

It includes the definitions of tables such as Researcher, SurveyStatus, DataProvider,
DataConnection, Collaboration, Project, Distribution, Respondent, and
DataProviderAccess, which are essential for managing the data related to surveys,
researchers, data providers, and respondents.

The module utilizes SQLAlchemy for ORM (Object-Relational Mapping) to facilitate
database operations, such as creating, reading, updating, and deleting records.
It also includes utility functions for database connection and session
management, leveraging Flask for web application integration.

Key Features:
- Definition of database models using SQLAlchemy's declarative base.
- Enumerations for SurveyStatus, DataProviderName, and DataProviderType to ensure data
    integrity.
- Relationships between tables to model complex data structures and associations.
- Utility functions for initializing database connections and sessions within a Flask
    app context.

Authors:
- Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
- Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)

Created on 2023-05-23 15:41
"""

from __future__ import annotations

import os
import time
import traceback
import uuid
from abc import abstractmethod
from datetime import datetime
from enum import Enum as StrEnum
from typing import TYPE_CHECKING, Any, ClassVar, Literal, TypedDict, override

from sonyflake import SonyFlake
from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    Engine,
    Enum,
    ForeignKey,
    Integer,
    Result,
    String,
    Text,
    TypeDecorator,
    create_engine,
    func,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Query, Session, mapped_column, relationship, sessionmaker

from ddsurveys.typings.models import BuiltinVariableDict, CustomVariableDict, FieldsDict

try:
    from ddsurveys.get_logger import get_logger
    from ddsurveys.utils import handle_env_file
except ImportError:
    from get_logger import get_logger
    from utils import handle_env_file

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask import Flask

    from ddsurveys.typings.models import (
        CollaborationDict,
        DataConnectionDict,
        DataConnectionPublicDict,
        DataProviderAccessDict,
        DataProviderDict,
        DistributionDict,
        ProjectDict,
        ProjectPublicDict,
        ResearcherDict,
        RespondentDict,
    )

logger = get_logger(__name__)

### Global variables
sony_flake: SonyFlake = SonyFlake()

### Load environment variables
handle_env_file()


class CreateEngineKwargsDict(TypedDict, total=False):
    # connect_args: Dict[Any, Any]
    # convert_unicode: bool
    # creator: _CreatorFnType | _CreatorWRecFnType
    # echo: _EchoFlagType
    # echo_pool: _EchoFlagType
    # enable_from_linting: bool
    # execution_options: _ExecuteOptions
    # future: bool
    # hide_parameters: bool
    # implicit_returning: bool
    # insertmanyvalues_page_size: int
    # isolation_level: IsolationLevel
    # json_deserializer: (...) -> Any
    # json_serializer: (...) -> Any
    # label_length: int | None
    # logging_name: str
    # max_identifier_length: int | None
    # max_overflow: int
    # module: Any | None
    # paramstyle: _ParamStyle | None
    # pool: Pool | None
    # poolclass: type[Pool] | None
    pool_logging_name: str
    pool_pre_ping: bool
    pool_size: int
    pool_recycle: int
    # pool_reset_on_return: ResetStyle | bool | Literal['commit', 'rollback'] | None
    pool_timeout: float
    pool_use_lifo: bool
    # plugins: list[str]
    # query_cache_size: int
    # use_insertmanyvalues: bool


class DBManager:
    """Singleton class for managing database connections and sessions."""

    ENGINE: Engine | None = None
    SESSION_MAKER: sessionmaker | None = None
    DB: Session | None = None

    create_engine_kwargs: ClassVar[CreateEngineKwargsDict] = {
        "pool_pre_ping": True,  # Check if connection is alive before using it
        "pool_recycle": 1800,  # Recycle connection after 30 minutes to avoid timeouts
        "pool_size": 10,  # Number of connections to maintain in the pool
    }

    @classmethod
    def get_engine(cls, app: Flask | None = None, database_url: str = "", *, force_new: bool = False) -> Engine:
        """Retrieves or initializes the SQLAlchemy engine for database connections.

        This function checks if the global `ENGINE` variable is already initialized.
        If not, it attempts to create a new engine using the database URL from the
        Flask application's configuration. If the Flask application is not provided
        or the configuration key is missing, it falls back to using the `DATABASE_URL`
        environment variable.

        Args:
            app: The Flask application instance. This is used to retrieve the database
                URL from the application's configuration. Defaults to None.
            database_url: The database URL to use for creating the engine.
                If provided, this URL will be used instead of the Flask application's
                configuration or the environment variable. Defaults to None.
            force_new: If True, forces the creation of a new engine even if he global
                `ENGINE` variable is already initialized.
                Defaults to False.

        Returns:
            Engine: The SQLAlchemy engine instance for database connections.
        """
        if cls.ENGINE is None or force_new:
            if database_url != "":
                cls.ENGINE = create_engine(url=database_url, **cls.create_engine_kwargs)
            elif app is not None:
                try:
                    cls.ENGINE = create_engine(url=app.config["DATABASE_URL"], **cls.create_engine_kwargs)
                except (AttributeError, KeyError):
                    cls.ENGINE = create_engine(url=os.getenv("DATABASE_URL"), **cls.create_engine_kwargs)
            else:
                cls.ENGINE = create_engine(url=os.getenv("DATABASE_URL"), **cls.create_engine_kwargs)
        return cls.ENGINE

    @classmethod
    def init_session(cls, app: Flask | None = None, database_url: str = "", *, force_new: bool = False) -> None:
        """Initializes the database session creator for the application.

        This function sets up the global SESSION_MAKER instance, which is used to create
        database sessions.

        Args:
            app: The Flask application instance.
                This is used to retrieve the database URL from the application's
                configuration.
                Defaults to None.
            database_url: The database URL to use for creating the
                engine.
                If provided, this URL will be used instead of the Flask application's
                configuration or the environment variable.
                Defaults to None.
            force_new: If True, forces the creation of a new engine and
                session maker even if they are already initialized.
                Defaults to False.

        Returns:
            None
        """
        cls.SESSION_MAKER = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.get_engine(app, database_url, force_new=force_new)
        )

    @classmethod
    def get_db(cls, app: Flask | None = None, database_url: str = "", *, force_new: bool = False) -> Session:
        """Provides a sqlalchemy.orm.session.Session instance for database operations.

        This function returns the global SessionLocal instance, which is configured
        to manage database sessions. The Session instance is used to create
        new sessions for interacting with the database, allowing for operations
        such as querying, adding, updating, and deleting records.

        Args:
            app (Flask, optional): The Flask application instance. This is used to
                                retrieve the database URL from the application's
                                configuration. Defaults to None.
            database_url (str, optional): The database URL to use for creating the engine.
                                        If provided, this URL will be used instead of the
                                        Flask application's configuration or the environment
                                        variable. Defaults to None.
            force_new (bool, optional): If True, forces the creation of a new engine and session maker
                                        even if they are already initialized. Defaults to False.

        Returns:
            Session: A configured Session instance for database operations.

        Raises:
            RuntimeError: If the session maker is not initialized and the function is called.
        """
        if cls.DB is None:
            if cls.SESSION_MAKER is None:
                cls.init_session(app=app, database_url=database_url, force_new=force_new)
            if cls.SESSION_MAKER is not None:
                cls.DB = cls.SESSION_MAKER()
            else:
                msg = "Database session maker is not initialized. Call init_session() first."
                raise RuntimeError(msg)
        return cls.DB

    @staticmethod
    def retry_query(
        query: Query, session: Session = None, retries: int = 3, *, orm_query: bool = True
    ) -> Result | None:
        """Executes a database query with retry logic in case of an OperationalError.

        This function attempts to execute the provided query using the given session.
        If an OperationalError occurs, it will retry the query up to the specified
        number of retries.

        If all retries fail, the exception is raised.

        Args:
            query: The SQLAlchemy query to be executed.
            session: The SQLAlchemy session to use for executing the query.
            retries: The number of times to retry the query in case of an error.
                Defaults to 3.
            orm_query: A flag indicating if the query is an ORM query (True)
                or a raw SQL query (False).

        Returns:
            Result | None: The result of the query execution if successful,
                or None if all retries fail.

        Raises:
            OperationalError: If the query fails after all retries.
        """
        for attempt in range(retries):
            try:
                if orm_query:
                    return query
                return session.execute(query)
            except OperationalError:
                if attempt < retries - 1:
                    logger.exception("Retrying query due to error.")
                    logger.debug(traceback.format_exc())
                    time.sleep(1)  # Wait a bit before retrying
                else:
                    logger.exception("Failed to execute query after all retries.")
                    logger.debug(traceback.format_exc())
                    raise
        return None


### Enums
class SurveyStatus(StrEnum):
    """Enumeration for different survey statuses.

    Attributes:
        Active (str): Represents an active survey status.
        Inactive (str): Represents an inactive survey status.
        Unknown (str): Represents an unknown survey status.
    """

    Active = "active"
    Inactive = "inactive"
    Unknown = "unknown"


# the enum entry "name" (ex. Fitbit) is used as name for the data provider
class DataProviderName(StrEnum):
    """Enumeration for different data provider names.

    Attributes:
        Fitbit (str): Represents the Fitbit data provider.
        Instagram (str): Represents the Instagram data provider.
        GitHub (str): Represents the GitHub data provider.
        DDS (str): Represents the DDS (Data-Driven Surveys) data provider.
        GoogleContacts (str): Represents the Google Contacts data provider.
    """

    Fitbit = "fitbit"
    Instagram = "instagram"
    GitHub = "github"
    DDS = "dds"
    GoogleContacts = "googlecontacts"


class DataProviderType(StrEnum):
    """Enumeration for different types of data providers.

    Attributes:
        generic (str): Represents a generic data provider type.
        oauth (str): Represents a data provider that uses OAuth for authentication.
        frontend (str): Represents a data provider that interacts with the frontend.
    """

    generic = "generic"
    oauth = "oauth"
    frontend = "frontend"


### TypedDicts
class SurveyPlatformFieldsDict(TypedDict):
    """Dictionary representation of survey platform fields."""

    survey_id: str
    survey_platform_api_key: str
    survey_name: str
    base_url: str
    survey_status: SurveyStatus | Literal["active", "inactive", "unknown"]
    mailing_list_id: str
    directory_id: str


### Database models
class Base(DeclarativeBase):
    """Base class for all database models."""

    type_annotation_map: ClassVar[dict[type, type[JSON]]] = {
        FieldsDict: JSON,
        SurveyPlatformFieldsDict: JSON,
        list[BuiltinVariableDict]: JSON,
        list[CustomVariableDict]: JSON,
    }

    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        """Creates a dictionary representation of a database row."""

    def to_public_dict(self) -> Mapping[str, Any]:
        """Creates a non-sensitive dictionary representation of a database row."""
        msg = "Subclasses must implement this method."
        raise NotImplementedError(msg)


class Researcher(Base):
    """Represents a researcher in the database.

    Attributes:
        id (int): The unique identifier for the researcher.
        firstname (str): The first name of the researcher.
        lastname (str): The last name of the researcher.
        email (str): The email address of the researcher.
        password (str): The hashed password of the researcher.
        collaborations (relationship): A relationship to the Collaboration table.
    """

    __tablename__ = "researcher"

    id: Mapped[int] = mapped_column(primary_key=True)

    firstname: Mapped[str] = mapped_column(String(255))
    lastname: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(512))  # Scrypt hashed password

    collaborations: Mapped[list[Collaboration]] = relationship("Collaboration", back_populates="researcher")

    @override
    def to_dict(self) -> ResearcherDict:
        """Converts the Researcher instance to a dictionary.

        Returns:
            ResearcherDict:
                A dictionary representation of the Researcher instance, including
                the id, firstname, lastname, and email.
        """
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
        }


class Collaboration(Base):
    """Collaboration between a researcher and a project."""

    __tablename__ = "collaboration"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"),
        primary_key=True,
    )
    researcher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("researcher.id", ondelete="CASCADE"),
        primary_key=True,
    )

    researcher: Mapped[Researcher] = relationship("Researcher", back_populates="collaborations")
    project: Mapped[Project] = relationship("Project", back_populates="collaborations")

    @override
    def to_dict(self) -> CollaborationDict:
        return {
            "project_id": self.project_id,
            "researcher": self.researcher.to_dict() if self.researcher else None,
        }


class DataProvider(Base):
    """Represents a data provider in the database.

    Attributes:
        data_provider_name (Enum):The name of the data provider, which serves as the
            primary key.
        data_provider_type (Enum): The type of the data provider, with a default value
            of 'generic'.
        name (str): The human-readable name of the data provider.
        data_connections (relationship): A relationship to the DataConnection table.
        data_provider_accesses (relationship): A relationship to the DataProviderAccess
            table.
    """

    __tablename__ = "data_provider"
    data_provider_name: Mapped[DataProviderName] = mapped_column(Enum(DataProviderName), primary_key=True)

    data_provider_type: Mapped[DataProviderType] = mapped_column(
        Enum(DataProviderType), default=DataProviderType.generic
    )
    name: Mapped[str] = mapped_column(String(255))

    data_connections: Mapped[list[DataConnection]] = relationship(
        "DataConnection",
        back_populates="data_provider",
    )
    data_provider_accesses: Mapped[list[DataProviderAccess]] = relationship(
        "DataProviderAccess",
        back_populates="data_provider",
    )

    @override
    def to_dict(self) -> DataProviderDict:
        """Converts the DataProvider instance to a dictionary.

        Returns:
            dict: A dictionary representation of the DataProvider instance, including
                  the name, data_provider_name, and data_provider_type.
        """
        return {
            "name": self.name,
            "data_provider_name": self.data_provider_name.value,
            "data_provider_type": self.data_provider_type.value,
        }


class DataConnection(Base):
    """Represents a data connection in the database.

    Attributes:
        project_id (str): The unique identifier for the project associated with the data
            connection.
        data_provider_name (Enum): The name of the data provider associated with the
            data connection.
        data_provider (relationship): A relationship to the DataProvider table.
        fields (JSON): The fields associated with the data connection.
        project (relationship): A relationship to the Project table.
    """

    __tablename__ = "data_connection"

    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project.id", ondelete="CASCADE"),
        primary_key=True,
    )
    data_provider_name: Mapped[DataProviderName] = mapped_column(
        Enum(DataProviderName),
        ForeignKey("data_provider.data_provider_name", ondelete="CASCADE"),
        primary_key=True,
    )

    fields: Mapped[FieldsDict] = mapped_column(JSON)

    data_provider: Mapped[DataProvider] = relationship("DataProvider", back_populates="data_connections")
    project: Mapped[Project] = relationship("Project", back_populates="data_connections")

    @override
    def to_dict(self) -> DataConnectionDict:
        """Converts the DataConnection instance to a dictionary.

        Returns:
            dict: A dictionary representation of the DataConnection instance, including
                  the project_id, data_provider_name, data_provider, and fields.
        """
        return {
            "project_id": self.project_id,
            "data_provider_name": self.data_provider_name.value,
            "data_provider": (self.data_provider.to_dict() if self.data_provider else None),
            "fields": self.fields,
        }

    @override
    def to_public_dict(self) -> DataConnectionPublicDict:
        """Converts the DataConnection instance to a public dictionary.

        Returns:
            dict: A public dictionary representation of the DataConnection instance,
                  including only the data_provider.
        """
        return {
            "data_provider": (self.data_provider.to_dict() if self.data_provider else None),
        }


class Project(Base):
    """Project model."""

    __tablename__ = "project"

    # TODO: change the project to use integer ids instead of uuid
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    short_id: Mapped[int] = mapped_column(BigInteger, default=lambda: sony_flake.next_id())
    name: Mapped[str] = mapped_column(String(255))
    survey_status: Mapped[SurveyStatus] = mapped_column(
        Enum(SurveyStatus), default=SurveyStatus.Unknown, nullable=False
    )
    survey_platform_name: Mapped[str] = mapped_column(String(255))
    survey_platform_fields: Mapped[SurveyPlatformFieldsDict] = mapped_column(JSON)
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_modified: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    last_synced: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    variables: Mapped[list[BuiltinVariableDict]] = mapped_column(JSON, default=[])
    custom_variables: Mapped[list[CustomVariableDict]] = mapped_column(JSON, default=[])

    data_connections: Mapped[list[DataConnection]] = relationship(
        "DataConnection",
        back_populates="project",
        cascade="all,delete",
    )
    collaborations: Mapped[list[Collaboration]] = relationship(
        "Collaboration",
        back_populates="project",
    )
    respondents: Mapped[list[Respondent]] = relationship(
        "Respondent",
        back_populates="project",
        cascade="all,delete",
    )
    data_provider_accesses: Mapped[list[DataProviderAccess]] = relationship(
        "DataProviderAccess",
        back_populates="project",
        cascade="all,delete",
    )

    @override
    def to_dict(self) -> ProjectDict:
        return {
            "id": self.id,
            "short_id": str(self.short_id),
            "name": self.name,
            "survey_status": self.survey_status.value,
            "survey_platform_name": self.survey_platform_name,
            "survey_platform_fields": self.survey_platform_fields,
            "last_modified": self.last_modified,
            "creation_date": self.creation_date,
            "last_synced": self.last_synced,
            "variables": self.variables,
            "custom_variables": self.custom_variables,
            "data_connections": [dc.to_dict() for dc in self.data_connections],
            "collaborations": [col.to_dict() for col in self.collaborations],
            "respondents": [res.to_dict() for res in self.respondents],
        }

    @override
    def to_public_dict(self) -> ProjectPublicDict:
        return {
            "id": self.id,
            "short_id": str(self.short_id),
            "name": self.name,
            "survey_name": (
                self.survey_platform_fields.get("survey_name", "") if self.survey_platform_fields is not None else ""
            ),
            "data_connections": [dc.to_public_dict() for dc in self.data_connections],
        }


class Distribution(Base):
    """Distribution model."""

    __tablename__ = "distribution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255))

    respondent: Mapped[Respondent] = relationship("Respondent", back_populates="distribution", uselist=False)

    @override
    def to_dict(self) -> DistributionDict:
        return {"id": self.id, "url": self.url}


class Respondent(Base):
    """Respondent model."""

    __tablename__ = "respondent"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id", ondelete="CASCADE"))
    distribution_id: Mapped[int] = mapped_column(Integer, ForeignKey("distribution.id", ondelete="CASCADE"))

    distribution: Mapped[Distribution] = relationship(
        "Distribution",
        back_populates="respondent",
        uselist=False,
        cascade="all, delete",
    )

    project: Mapped[Project] = relationship("Project", back_populates="respondents")

    data_provider_accesses: Mapped[list[DataProviderAccess]] = relationship(
        "DataProviderAccess", back_populates="respondent", cascade="all, delete"
    )

    @override
    def to_dict(self) -> RespondentDict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "distribution": self.distribution.to_dict() if self.distribution else None,
        }


class DataProviderAccess(Base):
    """DataProviderAccess model."""

    __tablename__ = "data_provider_access"

    data_provider_name: Mapped[DataProviderName] = mapped_column(
        Enum(DataProviderName),
        ForeignKey("data_provider.data_provider_name", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)
    respondent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("respondent.id", ondelete="CASCADE"), primary_key=True
    )

    access_token: Mapped[str] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=True)

    respondent: Mapped[Respondent] = relationship("Respondent", back_populates="data_provider_accesses")
    data_provider: Mapped[DataProvider] = relationship("DataProvider", back_populates="data_provider_accesses")
    project: Mapped[Project] = relationship("Project", back_populates="data_provider_accesses")

    @override
    def to_dict(self) -> DataProviderAccessDict:
        return {
            "respondent_id": self.respondent_id,
            "data_provider_name": self.data_provider_name.value,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
