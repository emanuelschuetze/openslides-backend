from tests.system.action.base import BaseActionTestCase


class MotionStatuteParagraphActionTest(BaseActionTestCase):
    def test_create(self) -> None:
        response = self.client.post(
            "/",
            json=[
                {
                    "action": "motion_statute_paragraph.create",
                    "data": [{"title": "test_Xcdfgee"}],
                }
            ],
        )
        self.assert_status_code(response, 200)
        self.assert_model_exists("motion_statute_paragraph/1")
        model = self.get_model("motion_statute_paragraph/1")
        assert model.get("title") == "test_Xcdfgee"
        assert model.get("weight") == 0

    def test_create_empty_data(self) -> None:
        response = self.client.post(
            "/", json=[{"action": "motion_statute_paragraph.create", "data": [{}]}],
        )
        self.assert_status_code(response, 400)
        self.assertIn(
            "data[0] must contain [\\'title\\'] properties", str(response.data),
        )

    def test_create_wrong_field(self) -> None:
        response = self.client.post(
            "/",
            json=[
                {
                    "action": "motion_statute_paragraph.create",
                    "data": [{"wrong_field": "text_AefohteiF8"}],
                }
            ],
        )
        self.assert_status_code(response, 400)
        self.assertIn(
            "data[0] must contain [\\'title\\'] properties", str(response.data),
        )