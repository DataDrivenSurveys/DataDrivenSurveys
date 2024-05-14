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
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

try:
    from .utils import handle_env_file
except ImportError:
    from utils import handle_env_file


sony_flake: SonyFlake = SonyFlake()

env = handle_env_file()

Base = declarative_base()

_engine: Engine = None


def get_engine(app: Flask = None) -> Engine:
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(url=app.config["DATABASE_URL"])
        except KeyError:
            _engine = create_engine(url=os.getenv("DATABASE_URL"))
    return _engine


SessionLocal: sessionmaker = None


def init_session(app: Flask) -> None:
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine(app))


def get_db() -> sessionmaker:
    return SessionLocal()


class Researcher(Base):
    __tablename__ = "researcher"
    id = Column(Integer, primary_key=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    email = Column(String(255))
    password = Column(String(512))  # Scrypt hashed password
    collaborations = relationship("Collaboration", back_populates="researcher")

    def to_dict(self) -> dict[str, Column[int] | Column[str]]:
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
        }


class SurveyStatus(PyEnum):
    Active = "active"
    Inactive = "inactive"
    Unknown = "unknown"


# the enum entry "name" (ex. Fitbit) is used as name for the data provider
class DataProviderName(PyEnum):
    Fitbit = "fitbit"
    Instagram = "instagram"
    GitHub = "github"
    Dds = "dds"


class DataProviderType(PyEnum):
    generic = "generic"
    oauth = "oauth"
    frontend = "frontend"


class DataProvider(Base):
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
        return {
            "name": self.name,
            "data_provider_name": self.data_provider_name.value,
            "data_provider_type": self.data_provider_type.value,
        }


class DataConnection(Base):
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
        return {
            "project_id": self.project_id,
            "data_provider_name": self.data_provider_name.value,
            "data_provider": (
                self.data_provider.to_dict() if self.data_provider else None
            ),
            "fields": self.fields,
        }

    def to_public_dict(self) -> dict[str, Any | None]:
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
