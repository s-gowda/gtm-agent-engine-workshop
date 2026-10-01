import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock

test_directory = Path(__file__).parent.resolve()
sys.path = [path for path in sys.path if Path(path or ".").resolve() != test_directory]
sys.path.insert(0, str(test_directory.parent))
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

import gtm_agent.gtm_agent as agent_module
from gtm_agent.gtm_agent import (
    build_prospect_profile,
    get_prospect,
    score_prospect,
    send_prospect_email,
)
from gtm_agent.gtm_records import OFFERINGS, PROSPECTS


SENSITIVE_FIELDS = (
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
)


def assert_no_sensitive_fields(value):
    serialized = json.dumps(value)
    for field in SENSITIVE_FIELDS:
        assert field not in serialized


def test_prospect_tools_and_scoring_exclude_billing_pii(monkeypatch):
    for prospect_id in PROSPECTS:
        profile = build_prospect_profile.invoke(prospect_id)
        cached_profile = build_prospect_profile.invoke(prospect_id)
        contact = get_prospect.invoke(prospect_id)
        assert_no_sensitive_fields(profile)
        assert_no_sensitive_fields(cached_profile)
        assert_no_sensitive_fields(contact)

    email = send_prospect_email.func(
        prospect=contact["prospect"],
        subject="Follow-up",
        body="Thanks for your time.",
        runtime=Mock(config={"metadata": {}}),
        from_rep={"name": "Rep", "email": "rep@example.com"},
    )
    assert email["status"] == "sent"

    scoring_llm = Mock()
    scoring_llm.invoke.return_value.model_dump.return_value = {"score": 80}
    monkeypatch.setattr(agent_module, "_scoring_llm", scoring_llm)

    profile = build_prospect_profile.invoke(next(iter(PROSPECTS)))
    profile["prospect_profile"]["billing_qualification"] = {
        "tax_id": "sensitive",
        "date_of_birth": "sensitive",
        "card_on_file": "sensitive",
        "credit_check_ref": "sensitive",
    }
    score_prospect.invoke({
        "prospect_profile": profile["prospect_profile"],
        "offering": next(iter(OFFERINGS.values())),
    })
    assert_no_sensitive_fields(scoring_llm.invoke.call_args.args)
