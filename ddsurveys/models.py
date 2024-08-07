#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the database models and utility functions for the Data-Driven Surveys platform. It includes the
definitions of tables such as Researcher, SurveyStatus, DataProvider, DataConnection, Collaboration, Project,
Distribution, Respondent, and DataProviderAccess, which are essential for managing the data related to surveys,
researchers, data providers, and respondents.

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
import os
from typing import Any
import uuid
from enum import Enum as PyEnum

from flask import Flask
from sonyflake import SonyFlake
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Engine,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

try:
    from .utils import handle_env_file
except ImportError:
    from utils import handle_env_file


# Global variables
sony_flake: SonyFlake = SonyFlake()

ENV = handle_env_file()

Base = declarative_base()


ENGINE: Engine = None
SESSION_MAKER: sessionmaker = None
DB: Session = None


def get_engine(app: Flask = None, database_url: str = None, force_new: bool = False) -> Engine:
    """
    Retrieves or initializes the SQLAlchemy engine for database connections.

    This function checks if the global `ENGINE` variable is already initialized.
    If not, it attempts to create a new engine using the database URL from the
    Flask application's configuration. If the Flask application is not provided
    or the configuration key is missing, it falls back to using the `DATABASE_URL`
    environment variable.

    Args:
        app (Flask, optional): The Flask application instance. This is used to
                               retrieve the database URL from the application's
                               configuration. Defaults to None.
        database_url (str, optional): The database URL to use for creating the engine.
                                      If provided, this URL will be used instead of
                                      the Flask application's configuration or the
                                      environment variable. Defaults to None.
        force_new (bool, optional): If True, forces the creation of a new engine even if
                                    the global `ENGINE` variable is already initialized.
                                    Defaults to False.

    Returns:
        Engine: The SQLAlchemy engine instance for database connections.
    """
    global ENGINE
    if ENGINE is None or force_new:
        if database_url is not None:
            ENGINE = create_engine(url=database_url)
        else:
            try:
                ENGINE = create_engine(url=app.config["DATABASE_URL"])
            except (AttributeError, KeyError):
                ENGINE = create_engine(url=os.getenv("DATABASE_URL"))
    return ENGINE


def init_session(app: Flask = None, database_url: str = None, force_new: bool = False) -> None:
    """
    Initializes the database session creator for the application.

    This function sets up the global SESSION_MAKER instance, which is used to create
    database sessions.

    Args:
        app (Flask, optional): The Flask application instance. This is used to retrieve
                               the database URL from the application's configuration.
                               Defaults to None.
        database_url (str, optional): The database URL to use for creating the engine.
                                      If provided, this URL will be used instead of the
                                      Flask application's configuration or the environment
                                      variable. Defaults to None.
        force_new (bool, optional): If True, forces the creation of a new engine and session maker
                                    even if they are already initialized. Defaults to False.

    Returns:
        None
    """
    global SESSION_MAKER
    SESSION_MAKER = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(app, database_url, force_new))


def get_db(app: Flask = None, database_url: str = None, force_new: bool = False) -> Session:
    """
    Provides a sqlalchemy.orm.session.Session instance for database operations.

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
    global DB
    if DB is None:
        if SESSION_MAKER is None:
            init_session(app, database_url, force_new)
        if SESSION_MAKER is not None:
            DB = SESSION_MAKER()
        else:
            raise RuntimeError("Database session maker is not initialized. Call init_session() first.")
    return DB


class Researcher(Base):
    """
    Represents a researcher in the database.

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
        """
        Converts the Researcher instance to a dictionary.

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
    """
    Enumeration for different survey statuses.

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
    """
    Enumeration for different data provider names.

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
    """
    Enumeration for different types of data providers.

    Attributes:
        generic (str): Represents a generic data provider type.
        oauth (str): Represents a data provider that uses OAuth for authentication.
        frontend (str): Represents a data provider that interacts with the frontend.
    """
    generic = "generic"
    oauth = "oauth"
    frontend = "frontend"


class DataProvider(Base):
    """
    Represents a data provider in the database.

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
    name = Column(String(255))
    data_connections = relationship("DataConnection", back_populates="data_provider")
    data_provider_accesses = relationship(
        "DataProviderAccess", back_populates="data_provider"
    )

    def to_dict(self) -> dict[str, Column[str]]:
        """
        Converts the DataProvider instance to a dictionary.

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
    """
    Represents a data connection in the database.

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
    data_provider = relationship("DataProvider", back_populates="data_connections")

    fields = Column(JSON)
    project = relationship("Project", back_populates="data_connections")

    def to_dict(
        self,
    ) -> dict[str, Column[str] | Column[JSON] | Column[None] | Column[Any]]:
        """
        Converts the DataConnection instance to a dictionary.

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

    def to_public_dict(self) -> dict[str, Any | None]:
        """
        Converts the DataConnection instance to a public dictionary.

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

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
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

    def to_public_dict(self) -> dict[str, Any]:
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

    def to_dict(self):
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

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "respondent_id": self.respondent_id,
            "data_provider_name": self.data_provider_name.value,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
