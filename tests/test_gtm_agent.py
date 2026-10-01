import unittest
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    def test_blocks_disqualified_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Priya Nair",
                "email": "priya.nair@northstarbiotech.com",
            },
            "Demo invitation",
            "Join us for a demo.",
            runtime=None,
            from_rep={},
        )

        self.assertEqual(result, {
            "status": "blocked",
            "error": "Prospect is disqualified; email not sent.",
        })

    def test_sends_non_disqualified_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-12853",
                "name": "Omar Okafor",
                "email": "omar.okafor@lakesideanalytics.com",
            },
            "Demo invitation",
            "Join us for a demo.",
            runtime=None,
            from_rep={},
        )

        self.assertEqual(result["status"], "sent")


if __name__ == "__main__":
    unittest.main()
