from typing import Any, Dict

from openslides_backend.permissions.permissions import Permissions
from tests.system.action.base import BaseActionTestCase


class MotionCreateForwarded(BaseActionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_model: Dict[str, Dict[str, Any]] = {
            "meeting/1": {"name": "name_XDAddEAW", "committee_id": 53},
            "meeting/2": {
                "name": "name_SNLGsvIV",
                "motions_default_workflow_id": 12,
                "committee_id": 52,
            },
            "user/1": {"meeting_ids": [1, 2]},
            "motion_workflow/12": {
                "name": "name_workflow1",
                "first_state_id": 34,
                "state_ids": [34],
            },
            "motion_state/34": {"name": "name_state34", "meeting_id": 2},
            "motion/12": {
                "title": "title_FcnPUXJB",
                "meeting_id": 1,
                "state_id": 34,
            },
            "committee/52": {"name": "name_EeKbwxpa"},
            "committee/53": {
                "name": "name_auSwgfJC",
                "forward_to_committee_ids": [52],
            },
        }

    def test_correct_origin_id_set(self) -> None:
        self.set_models(self.test_model)
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "meeting_id": 2,
                "origin_id": 12,
                "text": "test",
            },
        )
        self.assert_status_code(response, 200)
        model = self.get_model("motion/13")
        assert model.get("title") == "test_Xcdfgee"
        assert model.get("meeting_id") == 2
        assert model.get("origin_id") == 12

    def test_correct_origin_id_wrong_1(self) -> None:
        self.test_model["committee/53"]["forward_to_committee_ids"] = []
        self.set_models(self.test_model)
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "text": "text",
                "meeting_id": 2,
                "origin_id": 12,
            },
        )
        self.assert_status_code(response, 400)
        assert "Committee id 52 not in []" in response.json["message"]

    def test_missing_origin(self) -> None:
        self.set_models({"meeting/1": {"name": "meeting_1"}})
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "text": "text",
                "meeting_id": 222,
                "origin_id": 12,
            },
        )
        self.assert_status_code(response, 400)
        assert "Model 'motion/12' does not exist." in response.json["message"]

    def test_no_permissions(self) -> None:
        self.create_meeting()
        self.user_id = self.create_user("user")
        self.login(self.user_id)
        self.set_models({"group/4": {"meeting_id": 2}})
        self.set_user_groups(self.user_id, [3, 4])
        self.set_models(self.test_model)
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "meeting_id": 2,
                "origin_id": 12,
                "text": "test",
            },
        )
        self.assert_status_code(response, 403)
        assert "Missing permission: motion.can_create" in response.json["message"]

    def test_permissions(self) -> None:
        self.create_meeting()
        self.user_id = self.create_user("user")
        self.login(self.user_id)
        self.set_models({"group/4": {"meeting_id": 2}})
        self.set_user_groups(self.user_id, [3, 4])
        self.set_models(self.test_model)
        self.set_group_permissions(3, [Permissions.Motion.CAN_MANAGE])
        self.set_group_permissions(4, [Permissions.Motion.CAN_CREATE])
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "meeting_id": 2,
                "origin_id": 12,
                "text": "test",
            },
        )
        self.assert_status_code(response, 200)

    def test_no_permission_can_manage(self) -> None:
        self.create_meeting()
        self.user_id = self.create_user("user")
        self.login(self.user_id)
        self.set_models({"group/4": {"meeting_id": 2}})
        self.set_user_groups(self.user_id, [3, 4])
        self.set_models(self.test_model)
        self.set_group_permissions(3, [])
        self.set_group_permissions(4, [Permissions.Motion.CAN_CREATE])
        response = self.request(
            "motion.create_forwarded",
            {
                "title": "test_Xcdfgee",
                "meeting_id": 2,
                "origin_id": 12,
                "text": "test",
            },
        )
        self.assert_status_code(response, 403)
        assert "Missing permission: motion.can_manage" in response.json["message"]