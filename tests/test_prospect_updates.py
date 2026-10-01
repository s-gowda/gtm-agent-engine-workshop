import unittest
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class ProspectUpdateTests(unittest.TestCase):
    def setUp(self):
        self.prospect_id = "LEAD-39002"
        self.original_tech_stack = list(data_service.PROSPECTS[self.prospect_id]["tech_stack"])
        self.original_profile = data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        data_service.PROSPECTS[self.prospect_id]["tech_stack"] = self.original_tech_stack
        if self.original_profile is None:
            data_service._PROFILES.pop(self.prospect_id, None)
        else:
            data_service._PROFILES[self.prospect_id] = self.original_profile

    def test_update_persists_and_invalidates_cached_profile(self):
        build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        result = data_service.update_prospect_info(self.prospect_id, "Terraform")

        self.assertEqual(result["updated"], True)
        self.assertIn("Terraform", data_service.fetch_tech_stack(self.prospect_id))
        profile = build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        self.assertIn("Terraform", profile["prospect_profile"]["tech_stack"])

    def test_update_does_not_duplicate_existing_technology(self):
        data_service.update_prospect_info(self.prospect_id, "AWS")

        self.assertEqual(data_service.fetch_tech_stack(self.prospect_id).count("AWS"), 1)


if __name__ == "__main__":
    unittest.main()
