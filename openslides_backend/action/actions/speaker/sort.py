from typing import Any, Dict, Optional

from ....models.models import ListOfSpeakers, Speaker
from ....permissions.permissions import Permissions
from ....shared.filters import And, Filter, FilterOperator
from ...generics.update import UpdateAction
from ...mixins.linear_sort_mixin import LinearSortMixin
from ...mixins.singular_action_mixin import SingularActionMixin
from ...util.default_schema import DefaultSchema
from ...util.register import register_action
from ...util.typing import ActionData


@register_action("speaker.sort")
class SpeakerSort(LinearSortMixin, SingularActionMixin, UpdateAction):
    """
    Action to sort speakers.
    """

    model = Speaker()
    schema = DefaultSchema(Speaker()).get_linear_sort_schema(
        "speaker_ids",
        "list_of_speakers_id",
    )
    permission = Permissions.ListOfSpeakers.CAN_MANAGE
    permission_model = ListOfSpeakers()
    permission_id = "list_of_speakers_id"

    def get_updated_instances(self, action_data: ActionData) -> ActionData:
        filter: Optional[Filter] = None
        action_data = super().get_updated_instances(action_data)
        # Action data is an iterable with exactly one item
        instance = next(iter(action_data))
        if not filter:
            filter = And(
                FilterOperator(
                    "list_of_speakers_id", "=", instance["list_of_speakers_id"]
                ),
                FilterOperator("begin_time", "=", None),
            )
        add_to_db_instances: Dict[int, Any] = {}
        for key in self.datastore.additional_relation_models:
            if key.collection.collection == "speaker":
                add_to_db_instances[key.id] = {"id": key.id}

        yield from self.sort_linear(
            nodes=instance["speaker_ids"],
            filter_id=0,
            filter_str="",
            filter=filter,
            add_to_db_instances=add_to_db_instances,
        )
