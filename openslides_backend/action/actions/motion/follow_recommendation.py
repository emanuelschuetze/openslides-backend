import time
from typing import Any, Dict

from ....models.models import Motion
from ....permissions.permissions import Permissions
from ....services.datastore.commands import GetManyRequest
from ....shared.patterns import Collection, FullQualifiedId
from ...util.default_schema import DefaultSchema
from ...util.register import register_action
from ...util.typing import ActionData
from .set_state import MotionSetStateAction


@register_action("motion.follow_recommendation")
class MotionFollowRecommendationAction(MotionSetStateAction):

    model = Motion()
    schema = DefaultSchema(Motion()).get_update_schema()
    permission = Permissions.Motion.CAN_MANAGE

    def get_updated_instances(self, action_data: ActionData) -> ActionData:
        ids = [instance["id"] for instance in action_data]
        get_many_request = GetManyRequest(
            self.model.collection,
            ids,
            ["id", "recommendation_id", "recommendation_extension"],
        )
        gm_result = self.datastore.get_many([get_many_request])
        motions = gm_result.get(self.model.collection, {})

        for motion in motions.values():
            if motion.get("recommendation_id"):
                yield motion

    def update_instance(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        If motion has a recommendation_id, set the state to it and
        set state_extension.
        """
        recommendation_id = instance.pop("recommendation_id")
        instance["state_id"] = recommendation_id
        instance = super().update_instance(instance)
        recommendation = self.datastore.get(
            FullQualifiedId(Collection("motion_state"), recommendation_id),
            ["show_state_extension_field", "show_recommendation_extension_field"],
        )
        recommendation_extension = instance.pop("recommendation_extension", None)
        if (
            recommendation_extension is not None
            and recommendation.get("show_state_extension_field")
            and recommendation.get("show_recommendation_extension_field")
        ):
            instance["state_extension"] = recommendation_extension
        instance["last_modified"] = round(time.time())
        return instance
