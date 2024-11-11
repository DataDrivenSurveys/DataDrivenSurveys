"""Created on 2023-05-02 16:38.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.qualtrics import EmbeddedDataBlock

logger = get_logger(__name__)


type FlowType = dict[str, str | list[dict[str, Any]]]


class Flow:
    """Class representing a Qualtrics survey flow.

    Attributes:
        flow
        _custom_variables : CustomVariables
    """

    # TODO: Cleanup Flow class:
    #       - Handle correctly creating the flow if no flow is passed in __init__.
    #       - Use clearer property and attribute names.
    #       - Avoid duplicates in selected variables list.

    # TODO: add `is_full_flow()` to check if the flow is a full flow
    # TODO: add `flow_type()` property that returns the flow type
    # TODO: make variable namespaces start with `dds.`

    allowed_flow_types: tuple[str, ...] = (
        "Authenticator",
        "Block",
        "BlockRandomizer",
        "Branch",
        "Conjoint",
        "EmbeddedData",
        "EndSurvey",
        "Group",
        "QuotaCheck",
        " ReferenceSurvey",
        "Root",
        " Standard",
        "SupplementalData",
        "TableOfContents",
        "WebService",
    )

    def __init__(self, flow: dict) -> None:
        self._cv_block: EmbeddedDataBlock
        self._flow: FlowType
        self._cv_block_id: str
        self._cv_block_idx: int

        if flow["Type"] == "Root":
            self._flow = flow

            self._cv_block_id = self._identify_custom_variables_flow_id(flow, ("dds.",))
            self._cv_block_idx = self._get_block_index(self._cv_block_id)

            if self._cv_block_idx is None:
                self._cv_block_idx = 0
                self._cv_block = EmbeddedDataBlock(
                    flow_id=self._cv_block_id, variables_list=[]
                )
            else:
                self._cv_block = EmbeddedDataBlock(flow["Flow"][self._cv_block_idx])
                del self._flow["Flow"][self._cv_block_idx]
        else:  # Case where the flow is only an embedded data block
            self._flow = {
                "Flow": [],
                "FlowID": "FL_1",
                # "Properties": {"Count": 1, "RemovedFieldsets": []},
                "Properties": {"Count": 1, "RemovedFieldsets": []},
                "Type": "Root",
            }

            self._cv_block_id = "FL_2"
            self._cv_block_idx = 1

            self._cv_block = EmbeddedDataBlock(flow)

    @classmethod
    def _get_flow_ids(cls, flow_blocks: list | dict, flow_ids: list) -> None:
        """This function recursively searches the passed `flow_blocks` and appends all the ids to the `flow_ids` list.

        Args:
            flow_blocks
                The list of flow blocks that needs to be searched.
            flow_ids
                The list to which found flow ids will be appended.
        """
        if isinstance(flow_blocks, list):
            for block in flow_blocks:
                flow_ids.append(block["FlowID"])
                if "Flow" in block:
                    cls._get_flow_ids(block["Flow"], flow_ids)
        elif isinstance(flow_blocks, dict):
            flow_ids.append(flow_blocks["FlowID"])
            if "Flow" in flow_blocks:
                cls._get_flow_ids(flow_blocks["Flow"], flow_ids)
        else:
            msg = f"Expected flow_blocks to be of type list or dict. Received type: {type(flow_blocks)}"
            raise ValueError(
                msg
            )

    def _identify_custom_variables_flow_id(
        self, flow: dict, variables_namespaces: list = ()
    ) -> str:
        variables_namespaces = tuple(variables_namespaces) or ()

        if flow["Type"] == "EmbeddedData":
            return flow["FlowID"]
        elif flow["Type"] == "Root":
            flow_blocks = flow["Flow"]
        else:
            flow_blocks = flow

        flow_id = None
        candidates = []
        flow_ids = []
        # Check for existing embedded data blocks
        for block in flow_blocks:
            if block["Type"] == "EmbeddedData":
                candidates.append(block)
            self._get_flow_ids(block, flow_ids)

        # No existing custom variables block
        if len(candidates) > 0:
            valid_candidates = []
            for candidate in candidates:
                if all(
                    data["Field"].startswith(variables_namespaces)
                        for data in candidate["EmbeddedData"]
                ):
                    valid_candidates.append(candidate)
            if len(valid_candidates) > 1:
                logger.error("Multiple custom variable blocks found.")
                # raise ValueError(f"Only a single block can contain custom variables. "
                #                  f"Remove the extra custom variable blocks.")
            if len(valid_candidates) > 0:
                flow_id = valid_candidates[0]["FlowID"]

        if flow_id is None:
            flow_ids_nums = [int(id_.split("_")[1]) for id_ in flow_ids]
            flow_id = f"FL_{max(flow_ids_nums) + 1}"

        return flow_id

    def _get_block_index(self, flow_id: str) -> int | None:
        if self._flow["Type"] == "EmbeddedData":
            return 0

        for i, block in enumerate(self._flow["Flow"]):
            if block["FlowID"] == flow_id:
                return i

        return None

    @property
    def custom_variables_block_id(self) -> str:
        return self._cv_block_id

    @property
    def custom_variables(self) -> EmbeddedDataBlock:
        return self._cv_block

    @custom_variables.setter
    def custom_variables(self, value):
        # assert isinstance(value, list)
        # new_list = list()
        # for var in value:
        #     if isinstance(var, EmbeddedData):
        #         var = var.to_dict()
        #     new_list.append(var)
        self._cv_block["EmbeddedData"] = value

    @property
    def flow(self):
        return self.full_flow

    @property
    def full_flow(self):
        # variables_list = list()
        # for var in self.custom_variables:
        #     if isinstance(var, EmbeddedData):
        #         var = var.to_dict()
        #     variables_list.append(var)
        # self.custom_variables = variables_list
        #
        # if self._flow["Type"] == "EmbeddedData":
        #     flow = {
        #         "FlowID": "FL_1",
        #         "Type": "Root",
        #         "Properties": {
        #             "Count": 11,
        #             "RemovedFieldsets": []
        #         },
        #         "Flow": [self._flow]
        #     }
        # else:
        #     flow = self._flow

        flow = deepcopy(self._flow)
        flow["Flow"].insert(0, self.custom_variables.to_dict())
        flow["Properties"]["Count"] = len(flow["Flow"]) + 1

        return flow

    def to_dict(self) -> dict:
        flow = deepcopy(self._flow)
        flow["Flow"].insert(0, self.custom_variables.to_dict())
        flow["Properties"]["Count"] = len(flow["Flow"]) + 1

        return flow

    def __str__(self):
        return (
            f"{self.__class__.__name__}({len(self.flow['Flow'])} blocks, custom variables block id: "
            f"{self.custom_variables_block_id})"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.flow!r})"
