#!/usr/bin/env python3
"""This module defines the database models and utility functions for the project.

It includes the definitions of tables such as Researcher, SurveyStatus, DataProvider,
DataConnection, Collaboration, Project, Distribution, Respondent, and DataProviderAccess,
which are essential for managing the data related to surveys, researchers, data providers,
and respondents.

The module utilizes SQLAlchemy for ORM (Object-Relational Mapping) to facilitate database operations, such as creating,
reading, updating, and deleting records. It also includes utility functions for database connection and session
management, leveraging Flask for web application integration.

Key Features:
- Definition of database models using SQLAlchemy's declarative base.
- Enumerations for SurveyStatus, DataProviderName, and DataProviderType to ensure data integrity.
- Relationships between tables to model complex data structures and associations.
- Utility functions for initializing database connections and sessions within a Flask application context.

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
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, ClassVar

from sonyflake import SonyFlake
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Engine,
    Enum,
    ForeignKey,
    Integer,
    Result,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query, Session, declarative_base, relationship, sessionmaker

try:
    from ddsurveys.get_logger import get_logger
    from ddsurveys.utils import handle_env_file
except ImportError:
    from get_logger import get_logger
    from utils import handle_env_file

if TYPE_CHECKING:
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
        RespondentDict,
    )

logger = get_logger(__name__)

# Global variables
sony_flake: SonyFlake = SonyFlake()

# Load environment variables
handle_env_file()


class DBManager:
    ENGINE: Engine = None
    SESSION_MAKER: sessionmaker = None
    DB: Session = None

    engine_args: ClassVar[dict] = {
        "pool_pre_ping": True,  # Check if connection is alive before using it
        "pool_recycle": 1800,  # Recycle connection after 30 minutes to avoid timeouts
        "pool_size": 10,  # Number of connections to maintain in the pool
    }

    @classmethod
    def get_engine(cls, app: Flask = None, database_url: str = "", *, force_new: bool = False) -> Engine:
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
                cls.ENGINE = create_engine(url=database_url, **cls.engine_args)
            elif app is not None:
                try:
                    cls.ENGINE = create_engine(url=app.config["DATABASE_URL"], **cls.engine_args)
                except (AttributeError, KeyError):
                    cls.ENGINE = create_engine(url=os.getenv("DATABASE_URL"), **cls.engine_args)
            else:
                cls.ENGINE = create_engine(url=os.getenv("DATABASE_URL"), **cls.engine_args)
        return cls.ENGINE

    @classmethod
    def init_session(cls, app: Flask = None, database_url: str = "", *, force_new: bool = False) -> None:
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
            autocommit=False,
            autoflush=False,
            bind=cls.get_engine(app, database_url,
                                force_new=force_new)
        )

    @classmethod
    def get_db(cls, app: Flask = None, database_url: str = "", *, force_new: bool = False) -> Session:
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
    def retry_query(query: Query, session: Session = None, retries: int = 3, *, orm_query: bool = True) -> Result | None:
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


Base = declarative_base()


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

    id = Column(Integer, primary_key=True)

    firstname = Column(String(255))
    lastname = Column(String(255))
    email = Column(String(255))
    password = Column(String(512))  # Scrypt hashed password

    collaborations = relationship("Collaboration", back_populates="researcher")

    def to_dict(self) -> dict[str, Column[int] | Column[str]]:
        """Converts the Researcher instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Researcher instance, including
                  the id, firstname, lastname, and email.
        """
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
        }


class SurveyStatus(PyEnum):
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
class DataProviderName(PyEnum):
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


class DataProviderType(PyEnum):
    """Enumeration for different types of data providers.

    Attributes:
        generic (str): Represents a generic data provider type.
        oauth (str): Represents a data provider that uses OAuth for authentication.
        frontend (str): Represents a data provider that interacts with the frontend.
    """
    generic = "generic"
    oauth = "oauth"
    frontend = "frontend"


class DataProvider(Base):
    """Represents a data provider in the database.

    Attributes:
        data_provider_name (Enum): The name of the data provider, which serves as the primary key.
        data_provider_type (Enum): The type of the data provider, with a default value of 'generic'.
        name (str): The human-readable name of the data provider.
        data_connections (relationship): A relationship to the DataConnection table.
        data_provider_accesses (relationship): A relationship to the DataProviderAccess table.
    """
    __tablename__ = "data_provider"
    data_provider_name = Column(Enum(DataProviderName), primary_key=True)

    data_provider_type = Column(
        Enum(DataProviderType), default=DataProviderType.generic
    )
    name: str = Column(String(255))

    data_connections = relationship("DataConnection", back_populates="data_provider")
    data_provider_accesses = relationship(
        "DataProviderAccess", back_populates="data_provider"
    )

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
        project_id (str): The unique identifier for the project associated with the data connection.
        data_provider_name (Enum): The name of the data provider associated with the data connection.
        data_provider (relationship): A relationship to the DataProvider table.
        fields (JSON): The fields associated with the data connection.
        project (relationship): A relationship to the Project table.
    """
    __tablename__ = "data_connection"

    project_id = Column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True
    )
    data_provider_name = Column(
        Enum(DataProviderName),
        ForeignKey("data_provider.data_provider_name", ondelete="CASCADE"),
        primary_key=True,
    )

    fields = Column(JSON)

    data_provider = relationship("DataProvider", back_populates="data_connections")
    project = relationship("Project", back_populates="data_connections")

    def to_dict(self) -> DataConnectionDict:
        """Converts the DataConnection instance to a dictionary.

        Returns:
            dict: A dictionary representation of the DataConnection instance, including
                  the project_id, data_provider_name, data_provider, and fields.
        """
        return {
            "project_id": self.project_id,
            "data_provider_name": self.data_provider_name.value,
            "data_provider": (
                self.data_provider.to_dict() if self.data_provider else None
            ),
            "fields": self.fields,
        }

    def to_public_dict(self) -> DataConnectionPublicDict:
        """Converts the DataConnection instance to a public dictionary.

        Returns:
            dict: A public dictionary representation of the DataConnection instance,
                  including only the data_provider.
        """
        return {
            "data_provider": (
                self.data_provider.to_dict() if self.data_provider else None
            ),
        }


class Collaboration(Base):
    __tablename__ = "collaboration"
    project_id = Column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True
    )
    researcher_id = Column(
        Integer, ForeignKey("researcher.id", ondelete="CASCADE"), primary_key=True
    )

    researcher = relationship("Researcher", back_populates="collaborations")
    project = relationship("Project", back_populates="collaborations")

    def to_dict(self) -> CollaborationDict:
        return {
            "project_id": self.project_id,
            "researcher": self.researcher.to_dict() if self.researcher else None,
        }


class Project(Base):
    __tablename__ = "project"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    short_id = Column(BigInteger, default=lambda: sony_flake.next_id())
    name = Column(String(255))
    survey_status = Column(
        Enum(SurveyStatus), default=SurveyStatus.Unknown, nullable=False
    )
    survey_platform_name = Column(String(255))
    survey_platform_fields = Column(JSON)
    creation_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now(), onupdate=func.now())
    last_synced = Column(DateTime)
    variables = Column(JSON, default=[])
    custom_variables = Column(JSON, default=[])

    data_connections = relationship(
        "DataConnection", back_populates="project", cascade="all,delete"
    )
    collaborations = relationship("Collaboration", back_populates="project")
    respondents = relationship(
        "Respondent", back_populates="project", cascade="all,delete"
    )
    data_provider_accesses = relationship(
        "DataProviderAccess", back_populates="project", cascade="all,delete"
    )

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

    def to_public_dict(self) -> ProjectPublicDict:
        return {
            "id": self.id,
            "short_id": str(self.short_id),
            "name": self.name,
            "survey_name": (
                self.survey_platform_fields.get("survey_name", None)
                if self.survey_platform_fields is not None
                else None
            ),
            "data_connections": [dc.to_public_dict() for dc in self.data_connections],
        }


class Distribution(Base):
    __tablename__ = "distribution"
    id = Column(Integer, primary_key=True)
    url = Column(String(255))

    respondent = relationship(
        "Respondent", back_populates="distribution", uselist=False
    )

    def to_dict(self) -> DistributionDict:
        return {"id": self.id, "url": self.url}


class Respondent(Base):
    __tablename__ = "respondent"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("project.id", ondelete="CASCADE"))
    distribution_id = Column(Integer, ForeignKey("distribution.id", ondelete="CASCADE"))

    distribution = relationship(
        "Distribution",
        back_populates="respondent",
        uselist=False,
        cascade="all, delete",
    )

    project = relationship("Project", back_populates="respondents")

    data_provider_accesses = relationship(
        "DataProviderAccess", back_populates="respondent", cascade="all, delete"
    )

    def to_dict(self) -> RespondentDict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "distribution": self.distribution.to_dict() if self.distribution else None,
        }


class DataProviderAccess(Base):
    __tablename__ = "data_provider_access"

    data_provider_name = Column(
        Enum(DataProviderName),
        ForeignKey("data_provider.data_provider_name", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(String(255), nullable=False, primary_key=True)
    project_id = Column(
        String(36), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True
    )
    respondent_id = Column(
        String(36), ForeignKey("respondent.id", ondelete="CASCADE"), primary_key=True
    )

    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)

    respondent = relationship("Respondent", back_populates="data_provider_accesses")
    data_provider = relationship(
        "DataProvider", back_populates="data_provider_accesses"
    )
    project = relationship("Project", back_populates="data_provider_accesses")

    def to_dict(self) -> DataProviderAccessDict:
        return {
            "respondent_id": self.respondent_id,
            "data_provider_name": self.data_provider_name.value,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
