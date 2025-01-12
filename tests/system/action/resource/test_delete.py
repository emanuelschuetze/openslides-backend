from openslides_backend.permissions.management_levels import OrganizationManagementLevel
from tests.system.action.base import BaseActionTestCase


class ResourceDeleteActionTest(BaseActionTestCase):
    def test_delete_correct(self) -> None:
        self.set_models(
            {
                "resource/111": {"token": "srtgb123"},
                "user/1": {
                    "organization_management_level": OrganizationManagementLevel.CAN_MANAGE_ORGANIZATION
                },
            }
        )
        response = self.request("resource.delete", {"id": 111})

        self.assert_status_code(response, 200)
        self.assert_model_deleted("resource/111")

    def test_delete_wrong_id(self) -> None:
        self.set_models(
            {
                "resource/112": {"token": "srtgb123"},
                "user/1": {
                    "organization_management_level": OrganizationManagementLevel.CAN_MANAGE_ORGANIZATION
                },
            }
        )
        response = self.request("resource.delete", {"id": 111})
        self.assert_status_code(response, 400)
        model = self.get_model("resource/112")
        assert model.get("token") == "srtgb123"

    def test_delete_no_permissions(self) -> None:
        self.set_models(
            {
                "resource/111": {"token": "srtgb123"},
                "user/1": {
                    "organization_management_level": OrganizationManagementLevel.CAN_MANAGE_USERS
                },
            }
        )
        response = self.request("resource.delete", {"id": 111})

        self.assert_status_code(response, 403)
        self.assert_model_exists("resource/111")
