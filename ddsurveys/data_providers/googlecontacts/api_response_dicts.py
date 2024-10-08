#!/usr/bin/env python3
"""Created on 2024-07-05 12:53.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)

This module contains TypedDicts for the Google Contacts API responses.
"""
__all__ = [
    "MetadataDict",
    "NameDict",
    "NicknameDict",
    "PhotoDict",
    "BirthdayDict", "BirthdayInfoDict",
    "AddressDict",
    "EmailAddressDict",
    "PhoneNumberDict",
    "BiographyDict",
    "UrlDict",
    "OrganizationDict",
    "ContactGroupMembershipDict",
    "MembershipDict",
    "EventDict",
    "RelationDict",
    "ContactDict"
]

from typing import NotRequired, TypedDict


class SourceDict(TypedDict):
    type: str
    id: str
    etag: str
    updateTime: str


class MetadataDict(TypedDict):
    sources: list[SourceDict]
    objectType: str


class NameDict(TypedDict):
    metadata: dict
    displayName: str
    familyName: str
    givenName: str
    middleName: NotRequired[str]
    honorificPrefix: NotRequired[str]
    honorificSuffix: NotRequired[str]
    phoneticFamilyName: NotRequired[str]
    phoneticGivenName: NotRequired[str]
    phoneticMiddleName: NotRequired[str]
    displayNameLastFirst: str
    unstructuredName: str


class NicknameDict(TypedDict):
    metadata: dict
    value: str


class PhotoDict(TypedDict):
    metadata: dict
    url: str


class BirthdayInfoDict(TypedDict):
    year: NotRequired[int]
    month: int
    day: int


class BirthdayDict(TypedDict):
    metadata: dict
    date: BirthdayInfoDict


class AddressDict(TypedDict):
    metadata: dict
    formattedValue: str
    type: str
    formattedType: str
    streetAddress: str
    city: str
    region: str
    postalCode: str
    country: str
    countryCode: str


class EmailAddressDict(TypedDict):
    metadata: dict
    value: str
    type: str
    formattedType: str


class PhoneNumberDict(TypedDict):
    metadata: dict
    value: str
    type: str
    formattedType: str
    canonicalForm: NotRequired[str]


class BiographyDict(TypedDict):
    metadata: dict
    value: str
    contentType: str


class UrlDict(TypedDict):
    metadata: dict
    value: str
    type: str
    formattedType: str


class OrganizationDict(TypedDict):
    metadata: dict
    name: str
    department: NotRequired[str]
    title: NotRequired[str]


class ContactGroupMembershipDict(TypedDict):
    contactGroupId: str
    contactGroupResourceName: str


class MembershipDict(TypedDict):
    metadata: dict
    contactGroupMembership: ContactGroupMembershipDict


class EventDict(TypedDict):
    metadata: dict
    date: dict
    type: str
    formattedType: str


class RelationDict(TypedDict):
    metadata: dict
    person: str
    type: str
    formattedType: str


class ContactDict(TypedDict):
    resourceName: str
    etag: str
    metadata: MetadataDict
    names: list[NameDict]
    nicknames: list[NicknameDict]
    photos: list[PhotoDict]
    birthdays: list[BirthdayDict]
    addresses: list[AddressDict]
    emailAddresses: list[EmailAddressDict]
    phoneNumbers: list[PhoneNumberDict]
    biographies: list[BiographyDict]
    urls: list[UrlDict]
    organizations: list[OrganizationDict]
    memberships: list[MembershipDict]
    events: list[EventDict]
    relations: list[RelationDict]
