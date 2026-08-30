import hashlib
import json

import pytest


CONTRACT = "contracts/hearing_slot_coverage_allocator.py"
OWNER = "0x1111111111111111111111111111111111111111"
COMMENTER_A = "0x2222222222222222222222222222222222222222"
COMMENTER_B = "0x3333333333333333333333333333333333333333"
OTHER = "0x4444444444444444444444444444444444444444"
HEARING = "hearing-001"
TAXONOMY = "budget|safety|access"

COMMENTS = {
    "alpha": ("https://evidence.example.org/alpha.txt", "Budget and safety details.", "rev-1"),
    "bravo": ("https://evidence.example.org/bravo.txt", "Access and budget details. Source: report.", "rev-1"),
    "charlie": ("https://evidence.example.org/charlie.txt", "Safety details. Source: report.", "rev-1"),
    "delta": ("https://evidence.example.org/delta.txt", "Access details.", "rev-1"),
}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def llm_result(fields, status="ALLOCATED", reason="Bounded semantic assessment."):
    return json.dumps({"status": status, "comments": fields, "reason": reason})


def decision_fields(alpha=(3, False, ""), bravo=(5, True, ""), charlie=(2, True, "dup"), delta=(4, False, "")):
    return [
        {"comment_id": "alpha", "topic_mask": alpha[0], "citation_present": alpha[1], "duplicate_cluster": alpha[2]},
        {"comment_id": "bravo", "topic_mask": bravo[0], "citation_present": bravo[1], "duplicate_cluster": bravo[2]},
        {"comment_id": "charlie", "topic_mask": charlie[0], "citation_present": charlie[1], "duplicate_cluster": charlie[2]},
        {"comment_id": "delta", "topic_mask": delta[0], "citation_present": delta[1], "duplicate_cluster": delta[2]},
    ]


def one_field(comment_id="alpha", topic_mask=1, citation_present=False, duplicate_cluster=""):
    return [{
        "comment_id": comment_id,
        "topic_mask": topic_mask,
        "citation_present": citation_present,
        "duplicate_cluster": duplicate_cluster,
    }]


@pytest.fixture
def hearing(direct_deploy, direct_vm):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True
    contract = direct_deploy(CONTRACT)
    direct_vm.sender = OWNER
    contract.create_hearing(HEARING, TAXONOMY, digest(TAXONOMY))
    return contract, direct_vm


def add_comments(contract, vm, names=("alpha", "bravo", "charlie", "delta")):
    for index, name in enumerate(names):
        vm.sender = COMMENTER_A if index % 2 == 0 else COMMENTER_B
        url, body, revision = COMMENTS[name]
        contract.add_comment(HEARING, name, url, digest(body), revision)


def lock_with_comments(contract, vm, names=("alpha", "bravo", "charlie", "delta")):
    add_comments(contract, vm, names)
    vm.sender = OWNER
    contract.lock_comments(HEARING)


def mock_evidence(vm, names=("alpha", "bravo", "charlie", "delta")):
    for name in names:
        url, body, _revision = COMMENTS[name]
        vm.mock_web(r"evidence\.example\.org/" + name, {"status": 200, "body": body})


def test_create_add_lock_and_readback(hearing):
    contract, vm = hearing
    add_comments(contract, vm, ("alpha",))
    vm.sender = OWNER
    contract.lock_comments(HEARING)
    data = contract.read_allocation(HEARING)
    assert data["lifecycle"] == 2
    assert data["assessment_version"] == 1
    assert data["selected_comment_ids"] == []


def test_authorization_and_invalid_transition(hearing):
    contract, vm = hearing
    with pytest.raises(Exception):
        contract.lock_comments(HEARING)
    vm.sender = OTHER
    contract.add_comment(HEARING, "alpha", COMMENTS["alpha"][0], digest(COMMENTS["alpha"][1]), "rev-1")
    vm.sender = OWNER
    contract.lock_comments(HEARING)
    vm.sender = OTHER
    with pytest.raises(Exception):
        contract.close_hearing(HEARING)


def test_bounds_and_duplicate_guards(hearing):
    contract, vm = hearing
    add_comments(contract, vm, ("alpha",))
    with pytest.raises(Exception):
        vm.sender = COMMENTER_B
        contract.add_comment(HEARING, "alpha", COMMENTS["alpha"][0], digest(COMMENTS["alpha"][1]), "rev-1")
    for name in ("bravo", "charlie", "delta"):
        vm.sender = COMMENTER_A
        url, body, revision = COMMENTS[name]
        contract.add_comment(HEARING, name, url, digest(body), revision)
    vm.sender = COMMENTER_B
    with pytest.raises(Exception):
        contract.add_comment(HEARING, "echo", "https://evidence.example.org/" + ("e" * 600), "e" * 64, "rev-1")
    for blocked_url in ("https://127.0.0.1/echo.txt", "https://10.0.0.1/echo.txt", "http://evidence.example.org/echo.txt"):
        with pytest.raises(Exception):
            contract.add_comment(HEARING, "echo", blocked_url, "e" * 64, "rev-1")


def test_agreed_allocation_uses_exhaustive_optimum_and_readback(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm)
    mock_evidence(vm)
    fields = decision_fields(alpha=(1, False, ""), bravo=(1, False, ""), charlie=(2, True, ""), delta=(4, False, ""))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    data = contract.read_allocation(HEARING)
    assert data["lifecycle"] == 3
    assert data["selected_comment_ids"] == ["alpha", "charlie", "delta"]
    assert json.loads(data["decision_vector"])[2]["topic_mask"] == 2


def test_duplicate_cluster_is_excluded(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm)
    mock_evidence(vm)
    fields = decision_fields(bravo=(4, True, "same"), charlie=(3, True, "same"), delta=(2, False, ""))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    selected = contract.read_allocation(HEARING)["selected_comment_ids"]
    assert not ({"bravo", "charlie"} <= set(selected))


def test_consensus_normalizes_comment_order_and_cluster_token(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm)
    mock_evidence(vm)
    fields = decision_fields(
        alpha=(1, False, ""),
        bravo=(2, True, "cluster 1"),
        charlie=(4, True, "cluster-1"),
        delta=(1, False, ""),
    )
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result([fields[2], fields[0], fields[3], fields[1]]))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    assert contract.read_allocation(HEARING)["selected_comment_ids"] == ["alpha", "bravo"]


@pytest.mark.parametrize("invalid_cluster", ("---", "   ", "\t", "\n"))
def test_separator_only_cluster_token_fails_closed(hearing, invalid_cluster):
    contract, vm = hearing
    lock_with_comments(contract, vm)
    mock_evidence(vm)
    fields = decision_fields(alpha=(1, False, invalid_cluster))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    vm.sender = OWNER
    with pytest.raises(Exception):
        contract.allocate_slots(HEARING)
    assert contract.read_allocation(HEARING)["lifecycle"] == 2


def test_allocated_without_topic_is_canonical_unresolved(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    mock_evidence(vm, ("alpha",))
    vm.mock_llm(
        r"You assess a bounded hearing comment set",
        llm_result(one_field(topic_mask=0), "ALLOCATED", "No stable topic was established."),
    )
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    data = contract.read_allocation(HEARING)
    assert data["lifecycle"] == 4
    assert data["selected_comment_ids"] == []


@pytest.mark.parametrize(
    ("body", "expected_citation"),
    (("budget safety httpish", False), ("budget safety https://example.org/source", True)),
)
def test_repeated_evidence_citation_marker_is_bounded(hearing, body, expected_citation):
    contract, vm = hearing
    body_digest = digest(body)
    vm.sender = COMMENTER_A
    contract.add_comment(
        HEARING, "alpha", "https://evidence.example.org/repeat-a", body_digest, "rev-1"
    )
    vm.sender = COMMENTER_B
    contract.add_comment(
        HEARING, "bravo", "https://evidence.example.org/repeat-b", body_digest, "rev-1"
    )
    vm.sender = OWNER
    contract.lock_comments(HEARING)
    vm.mock_web(r"evidence\.example\.org/repeat-a", {"status": 200, "body": body})
    vm.mock_web(r"evidence\.example\.org/repeat-b", {"status": 200, "body": body})
    vm.mock_llm(
        r"You assess a bounded hearing comment set",
        llm_result(
            [
                {"comment_id": "alpha", "topic_mask": 3, "citation_present": True, "duplicate_cluster": "model output !!!"},
                {"comment_id": "bravo", "topic_mask": 3, "citation_present": True, "duplicate_cluster": "model output !!!"},
            ]
        ),
    )
    contract.allocate_slots(HEARING)
    decision = json.loads(contract.read_allocation(HEARING)["decision_vector"])
    assert [item["citation_present"] for item in decision] == [expected_citation, expected_citation]


def test_citation_then_lexicographic_tie_break(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm)
    mock_evidence(vm)
    fields = decision_fields(alpha=(1, False, "a"), bravo=(2, True, "b"), charlie=(1, False, "a"), delta=(2, False, "b"))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    assert contract.read_allocation(HEARING)["selected_comment_ids"] == ["alpha", "bravo"]


def test_unresolved_is_fail_closed_and_retry_increments_version(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    mock_evidence(vm, ("alpha",))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(one_field(), "UNRESOLVED", "Evidence is ambiguous."))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    first = contract.read_allocation(HEARING)
    assert first["lifecycle"] == 4
    assert first["selected_comment_ids"] == []
    locked_digest = first["evidence_digest"]
    vm.clear_mocks()
    mock_evidence(vm, ("alpha",))
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(one_field()))
    contract.allocate_slots(HEARING)
    second = contract.read_allocation(HEARING)
    assert second["assessment_version"] == 2
    assert second["evidence_digest"] == locked_digest


def test_retry_consensus_failure_versions_prior_unresolved(hearing, monkeypatch):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    mock_evidence(vm, ("alpha",))
    vm.mock_llm(
        r"You assess a bounded hearing comment set",
        llm_result(one_field(), "UNRESOLVED", "Evidence is ambiguous."),
    )
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    prior = contract.read_allocation(HEARING)

    def fail_consensus(_leader, _validator):
        raise RuntimeError("consensus failure")

    import genlayer.gl.vm as gl_vm

    monkeypatch.setattr(gl_vm, "run_nondet_unsafe", fail_consensus)
    contract.allocate_slots(HEARING)
    retry = contract.read_allocation(HEARING)
    assert retry["assessment_version"] == 2
    assert retry["lifecycle"] == 4
    assert retry["evidence_digest"] == prior["evidence_digest"]
    assert retry["decision_vector"] == prior["decision_vector"]
    assert retry["selected_comment_ids"] == []


def test_bad_evidence_fails_without_false_allocation(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    vm.mock_web(r"evidence\.example\.org/alpha", {"status": 200, "body": "changed"})
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    assert contract.read_allocation(HEARING)["lifecycle"] == 4
    vm.clear_mocks()
    mock_evidence(vm, ("alpha",))
    vm.mock_llm(r"You assess a bounded hearing comment set", "{}")
    contract.allocate_slots(HEARING)
    assert contract.read_allocation(HEARING)["lifecycle"] == 4


def test_validator_differential_rejects_changed_consequence_field(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    mock_evidence(vm, ("alpha",))
    fields = one_field()
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    vm.sender = OWNER
    contract.allocate_slots(HEARING)
    assert vm.run_validator() is True
    altered = one_field(topic_mask=2)
    assert vm.run_validator(
        leader_result={"status": "ALLOCATED", "comments": altered, "reason": "changed"}
    ) is False


def test_close_requires_allocated_and_then_is_terminal(hearing):
    contract, vm = hearing
    lock_with_comments(contract, vm, ("alpha",))
    vm.sender = OWNER
    with pytest.raises(Exception):
        contract.close_hearing(HEARING)
    mock_evidence(vm, ("alpha",))
    fields = one_field()
    vm.mock_llm(r"You assess a bounded hearing comment set", llm_result(fields))
    contract.allocate_slots(HEARING)
    contract.close_hearing(HEARING)
    assert contract.read_allocation(HEARING)["lifecycle"] == 5
    with pytest.raises(Exception):
        contract.close_hearing(HEARING)
