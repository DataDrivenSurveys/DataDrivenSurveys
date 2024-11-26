"""Created on 2024-07-05 13:23.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from typing import TYPE_CHECKING, Any, ClassVar

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.typings.data_providers.variables import DataOriginDict
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from ddsurveys.data_providers.googlecontacts import GoogleContactsDataProvider

data_origin: list[DataOriginDict] = [
    {
        "method": "get",
        "endpoint": "https://people.googleapis.com/v1/resourceName=people/me",
        "documentation": "https://developers.google.com/people/api/rest/v1/people/get",
    }
]


class People(DataCategory["GoogleContactsDataProvider"]):
    data_origin: ClassVar[list[DataOriginDict]] = data_origin

    custom_variables_enabled = False

    def fetch_data(self) -> list[dict[str, Any]]:
        return self.data_provider.contacts

    cv_attributes = []

    builtin_variables: ClassVar[list[list[BuiltInVariable["GoogleContactsDataProvider"]]]] = [
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="total_contacts",
            label="Total number of contacts",
            description="The total number of contacts that a respondent has.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The total number of contacts that a respondent has. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_contacts,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_first_name",
            label="Number of contacts with a first name",
            description="The number of contacts that a respondent has with a first name.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a first name. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_first_name,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_last_name",
            label="Number of contacts with a last name",
            description="The number of contacts that a respondent has with a last name.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a last name. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_last_name,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_nickname",
            label="Number of contacts with a nickname",
            description="The number of contacts that a respondent has with a nickname.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a nickname. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_nickname,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_organization",
            label="Number of contacts with a company name",
            description="The number of contacts that a respondent has with an organization.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with an organization. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_organization,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_company_or_title",
            label="Number of contacts with a company name or job title",
            description="The number of contacts that a respondent has with company name or job title.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a company name or job title. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_company_or_title,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_relations",
            label="Number of contacts with related persons",
            description="The number of contacts that a respondent has with related persons.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with related persons. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_relations,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_email_addresses",
            label="Number of contacts with email address(es)",
            description="The number of contacts that a respondent has with email address(es).",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with email address(es). "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_email_addresses,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_phone_numbers",
            label="Number of contacts with phone number(s)",
            description="The number of contacts that a respondent has with phone number(s).",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with phone number(s). "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_phone_numbers,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_photos",
            label="Number of contacts with photo(s)",
            description="The number of contacts that a respondent has with photo(s).",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with photo(s). "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_photos,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_birthday",
            label="Number of contacts with a birthday (year optional)",
            description="The number of contacts that a respondent has with a birthday (year optional).",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a birthday (year optional). "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_birthday,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_addresses",
            label="Number of contacts with addresses",
            description="The number of contacts that a respondent has with addresses.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with addresses. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_addresses,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_biographies",
            label="Number of contacts with notes/biographies",
            description="The number of contacts that a respondent has with notes/biographies.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with notes/biographies. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_biographies,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_0_phone_numbers",
            label="Number of contacts with no phone numbers",
            description="The number of contacts that a respondent has with no phone numbers.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with no phone numbers. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_0_phone_numbers,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_1_phone_numbers",
            label="Number of contacts with one phone number",
            description="The number of contacts that a respondent has with one phone number.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with one phone number. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_1_phone_numbers,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_2_phone_numbers",
            label="Number of contacts with two phone numbers",
            description="The number of contacts that a respondent has with two phone numbers.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with two phone numbers. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_2_phone_numbers,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_3_or_more_phone_numbers",
            label="Number of contacts with three or more phone numbers",
            description="The number of contacts that a respondent has with three or more phone numbers.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with three or more phone numbers. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_3_or_more_phone_numbers,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_birthday_year",
            label="Number of contacts with birthdays that also include the year",
            description="The number of contacts that a respondent has with birthdays that also include the year.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with birthdays that also include the year. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_birthday_year,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_biographies_few_words",
            label="Number of contacts with notes a few words long",
            description="The number of contacts that a respondent has with notes a few words long.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with notes a few words long. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_biographies_few_words,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_biographies_few_sentences",
            label="Number of contacts with notes a few sentences long",
            description="The number of contacts that a respondent has with notes a few sentences long.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with notes a few sentences long. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_biographies_few_sentences,
            data_origin=data_origin,
        ),
        BuiltInVariable["GoogleContactsDataProvider"].create_instances(
            name="num_with_biographies_few_paragraphs",
            label="Number of contacts with notes a few paragraphs long",
            description="The number of contacts that a respondent has with notes a few paragraphs long.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with notes a few paragraphs long. "
            "It will always be a whole number greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_biographies_few_paragraphs,
            data_origin=data_origin,
        ),
    ]
