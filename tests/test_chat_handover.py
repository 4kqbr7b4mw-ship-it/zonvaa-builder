from pathlib import Path
import subprocess

from builder.chat_handover import ChatHandover


PROJECT_ROOT = Path(__file__).resolve().parents[1]


WORKING_CONTEXT = """# Rules

## Kanonischer Arbeitskontext

- Der Mensch bestimmt das fachliche Ziel und die Produktgrenzen.
- Der Chief Architect formuliert Aufträge und bewertet Ergebnisse.
- Der Builder schützt und validiert, entscheidet aber nicht fachlich.
- Codex implementiert, testet und berichtet.
- Der Nutzer ist kein manueller Terminal-, Such-, Prüf- oder Transportweg.
- Commit und Push benötigen getrennte menschliche Freigaben.
- ZONVAA V2 ist aktiv. ZONVAA V1 ist ausschließlich Archiv.
- Keine automatische Architekturentscheidung.
- Keine ungefragten schreibenden Git-Operationen.
- Fachlich kohärente Teilbausteine dürfen als reviewbares Paket bearbeitet
  werden; Teilberichte und Tests bleiben getrennt, die Integration wird geprüft.
  Blockierte Teile werden nicht umgedeutet oder durch Ersatzarchitektur umgangen.

## Other

Not part of the handover.
"""

PRODUCT_STATUS = """# Status

## Aktives Repository

- Produktlinie: ZONVAA V2
- Erwarteter Branch: `builder-reset-v2`
- ZONVAA V1: ausschließlich Archiv

## Abgeschlossene Produktbausteine

- Guardian Understanding Core v1
- Guardian Understanding Model v2
- Guardian Understanding Proposal Layer v1
- Guardian Clarification Resolution v1
- Guardian Life Decision Conversation v1: Vorsorgevollmacht
- Guardian Life Decision Conversation v2: Mehrzügige Vorsorgevollmacht-Gesprächsführung
- Guardian Life Decision Journey v1: Vorsorgevollmacht
- Power-of-Attorney Professional Review Preparation
- Guardian Life Decision Experience v1: Vorsorgevollmacht
- Guardian Life Decision v1: Patientenverfügung
- Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie
- Family Care Cross-Domain Scenario Validation v1
- Family Care End-to-End Reference Journey v1
- Guardian Family Care Review UI v1 (lokales internes Prüfwerkzeug)
- Guardian Answer Boundary Contracts v1
- Guardian Source Chain Contracts v1
- Guardian Classification Contract v1
- Guardian Answer Foundation Integration v1
- Guardian Controlled Orientation Package v1
- Guardian Personal Preparation Package v1
- Guardian Professional Decision Boundary Package v1
- End-to-End Guardian Answer Reference Journey v1

## Aktueller fachlicher Stand

- Der nächste Produktbaustein ist noch nicht bestimmt.

## Bewusste Produktgrenzen

- Keine automatische Semantik
- Keine Intent Engine
- Kein Routing
- Keine Decision Engine
- Keine automatische Fähigkeitsaktivierung
- Keine automatische Workflow-Aktivierung
- Kein persistentes Guardian Memory
- Keine LLM-Integration
- Keine Confidence-Scores

## Nächster noch nicht begonnener Schritt

Noch nicht bestimmt. Der Handover wählt keinen Produktbaustein automatisch aus.
"""


def git(repository, *arguments):
    return subprocess.run(
        ("git",) + arguments,
        cwd=str(repository),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def repository(tmp_path, remote=True, ahead=False):
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-b", "builder-reset-v2")
    git(root, "config", "user.name", "ZONVAA Test")
    git(root, "config", "user.email", "zonvaa@example.test")
    (root / "AGENTS.md").write_text(WORKING_CONTEXT, encoding="utf-8")
    status = root / "knowledge" / "project" / "current-product-status.md"
    status.parent.mkdir(parents=True)
    status.write_text(PRODUCT_STATUS, encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "initial")
    if remote:
        git(
            root,
            "update-ref",
            "refs/remotes/origin/builder-reset-v2",
            "HEAD",
        )
    if ahead:
        (root / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        git(root, "add", "tracked.txt")
        git(root, "commit", "-m", "ahead")
    return root


def test_handover_contains_canonical_working_method_and_product_status(tmp_path):
    root = repository(tmp_path)

    output = ChatHandover(root).render()

    assert "Der Mensch bestimmt das fachliche Ziel" in output
    assert "Der Chief Architect formuliert" in output
    assert "Codex implementiert, testet und berichtet" in output
    assert "Guardian Understanding Core v1" in output
    assert "Guardian Understanding Model v2" in output
    assert "Guardian Understanding Proposal Layer v1" in output
    assert "Guardian Clarification Resolution v1" in output
    assert "Guardian Life Decision Conversation v1: Vorsorgevollmacht" in output
    assert "Guardian Life Decision Conversation v2" in output
    assert "Guardian Life Decision Journey v1" in output
    assert "Power-of-Attorney Professional Review Preparation" in output
    assert "Guardian Life Decision Experience v1" in output
    assert "Guardian Life Decision v1: Patientenverfügung" in output
    assert "Guardian Cross-Domain Life Situation v1" in output
    assert "Family Care Cross-Domain Scenario Validation v1" in output
    assert "Family Care End-to-End Reference Journey v1" in output
    assert "Guardian Family Care Review UI v1" in output
    assert "Guardian Answer Boundary Contracts v1" in output
    assert "Guardian Source Chain Contracts v1" in output
    assert "Guardian Classification Contract v1" in output
    assert "Guardian Answer Foundation Integration v1" in output
    assert "Guardian Controlled Orientation Package v1" in output
    assert "Guardian Personal Preparation Package v1" in output
    assert "Guardian Professional Decision Boundary Package v1" in output
    assert "End-to-End Guardian Answer Reference Journey v1" in output
    assert "reviewbares Paket" in output
    assert "Ersatzarchitektur" in output
    assert "Keine Intent Engine" in output


def test_repository_canonical_status_matches_confirmed_product_state():
    output = ChatHandover(PROJECT_ROOT).render()

    assert "Fachlich kohärente, architektonisch geklärte Teilbausteine" in output
    assert "Bericht und Tests bleiben je Teilbaustein" in output
    assert "nicht umgedeutet oder durch Ersatzarchitektur umgangen" in output

    expected_in_order = (
        "Guardian Understanding Core v1",
        "Guardian Understanding Model v2",
        "Guardian Understanding Proposal Layer v1",
        "Guardian Clarification Resolution v1",
        "Guardian Life Decision Conversation v1: Vorsorgevollmacht",
        "Guardian Life Decision Conversation v2: Mehrzügige Vorsorgevollmacht-Gesprächsführung",
        "Guardian Life Decision Journey v1: Vorsorgevollmacht",
        "Power-of-Attorney Professional Review Preparation",
        "Guardian Life Decision Experience v1: Vorsorgevollmacht",
        "Guardian Life Decision v1: Patientenverfügung",
        "Guardian Cross-Domain Life Situation v1: Pflegefall in der Familie",
        "Family Care Cross-Domain Scenario Validation v1",
        "Family Care End-to-End Reference Journey v1",
        "Guardian Family Care Review UI v1 (lokales internes Prüfwerkzeug)",
        "Guardian Answer Boundary Contracts v1",
        "Guardian Source Chain Contracts v1",
        "Guardian Classification Contract v1",
        "Guardian Answer Foundation Integration v1",
        "Guardian Controlled Orientation Package v1",
        "Guardian Personal Preparation Package v1",
        "Guardian Professional Decision Boundary Package v1",
        "End-to-End Guardian Answer Reference Journey v1",
        "Keine automatische Semantik",
        "Keine Intent Engine",
        "Kein Routing",
        "Keine Decision Engine",
        "Keine automatische Fähigkeitsaktivierung",
        "Keine automatische Workflow-Aktivierung",
        "Kein persistentes Guardian Memory",
        "Keine LLM-Integration",
        "Keine Confidence-Scores",
        "Noch nicht bestimmt",
    )
    positions = [output.index(value) for value in expected_in_order]
    assert positions == sorted(positions)
    assert git(PROJECT_ROOT, "rev-parse", "HEAD") in output


def test_handover_reads_local_and_remote_head_at_runtime(tmp_path):
    root = repository(tmp_path, ahead=True)
    local_head = git(root, "rev-parse", "HEAD")
    remote_head = git(
        root,
        "rev-parse",
        "refs/remotes/origin/builder-reset-v2",
    )

    output = ChatHandover(root).render()

    assert "- Lokaler HEAD: `{}`".format(local_head) in output
    assert "- Remote-HEAD: `{}`".format(remote_head) in output
    assert "- Ahead/Behind: 0 behind / 1 ahead" in output


def test_handover_reports_clean_and_dirty_working_tree(tmp_path):
    root = repository(tmp_path)
    assert "- Arbeitsbaum: sauber" in ChatHandover(root).render()

    (root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    output = ChatHandover(root).render()

    assert "- Arbeitsbaum: nicht sauber" in output
    assert "?? dirty.txt" in output


def test_handover_reports_missing_remote_without_inventing_values(tmp_path):
    root = repository(tmp_path, remote=False)

    output = ChatHandover(root).render()

    assert "- Remote-HEAD: `nicht verfügbar`" in output
    assert "- Ahead/Behind: nicht verfügbar" in output


def test_handover_reports_branch_mismatch(tmp_path):
    root = repository(tmp_path)
    git(root, "branch", "-m", "other-branch")

    output = ChatHandover(root).render()

    assert "- Branch: `other-branch`" in output
    assert (
        "- Branch-Abweichung: erwartet `builder-reset-v2`, "
        "tatsächlich `other-branch`"
    ) in output


def test_handover_is_read_only_for_files_index_head_and_remote(tmp_path):
    root = repository(tmp_path, ahead=True)
    (root / "dirty.txt").write_text("unchanged\n", encoding="utf-8")
    before_status = git(root, "status", "--short", "--untracked-files=all")
    before_head = git(root, "rev-parse", "HEAD")
    before_remote = git(
        root,
        "rev-parse",
        "refs/remotes/origin/builder-reset-v2",
    )
    before_files = {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

    ChatHandover(root).render()

    after_files = {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert after_files == before_files
    assert git(root, "status", "--short", "--untracked-files=all") == before_status
    assert git(root, "diff", "--cached") == ""
    assert git(root, "rev-parse", "HEAD") == before_head
    assert (
        git(root, "rev-parse", "refs/remotes/origin/builder-reset-v2")
        == before_remote
    )


def test_handover_uses_only_read_only_git_commands(tmp_path):
    root = repository(tmp_path)
    calls = []

    def recording_runner(arguments, cwd):
        calls.append(tuple(arguments))
        return subprocess.run(
            tuple(arguments),
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
        )

    ChatHandover(root, runner=recording_runner).render()

    assert calls
    assert {call[1] for call in calls} <= {
        "branch",
        "rev-list",
        "rev-parse",
        "status",
    }
    assert not any(
        forbidden in call
        for call in calls
        for forbidden in ("add", "commit", "push")
    )


def test_handover_does_not_select_a_next_product_component(tmp_path):
    root = repository(tmp_path)

    output = ChatHandover(root).render()

    next_section = output.split(
        "## Nächster noch nicht begonnener Schritt",
        1,
    )[1]
    assert "Noch nicht bestimmt" in next_section
    assert "automatisch aus" in next_section


def test_handover_never_presents_v1_as_active_repository(tmp_path):
    root = repository(tmp_path)

    output = ChatHandover(root).render()

    assert "# ZONVAA V2 Chat-Übergabe" in output
    assert "ZONVAA V1 ist ausschließlich Archiv" in output
    assert "ZONVAA V1 Chat-Übergabe" not in output


def test_handover_has_deterministic_semantic_section_order(tmp_path):
    root = repository(tmp_path)

    first = ChatHandover(root).render()
    second = ChatHandover(root).render()

    assert first == second
    headings = (
        "## Repository",
        "## Kanonische Arbeitsweise",
        "## Abgeschlossene Produktbausteine",
        "## Aktueller fachlicher Stand",
        "## Bewusste Produktgrenzen",
        "## Nächster noch nicht begonnener Schritt",
    )
    assert [first.index(heading) for heading in headings] == sorted(
        first.index(heading) for heading in headings
    )
