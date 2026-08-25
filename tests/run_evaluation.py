import json
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_URL}/chat"

CASES_FILE = Path("evaluation/visible-cases.json")


# ============================================================
# 5 ADDITIONAL QUERIES
# ============================================================

ADDITIONAL_CASES = [
    {
        "id": "additional-return-condition",
        "messages": [
            {
                "role": "user",
                "content": "Can I return a backpack that I already used once?"
            }
        ],
    },
    {
        "id": "additional-international-shipping",
        "messages": [
            {
                "role": "user",
                "content": "Do you ship to Australia?"
            }
        ],
    },
    {
        "id": "additional-order-status",
        "messages": [
            {
                "role": "user",
                "content": "Can you check ORD-1007 for me?"
            }
        ],
    },
    {
        "id": "additional-order-missing-id",
        "messages": [
            {
                "role": "user",
                "content": "Can you tell me where my package is?"
            }
        ],
    },
    {
        "id": "additional-warranty",
        "messages": [
            {
                "role": "user",
                "content": "How long is the warranty on bags?"
            }
        ],
    },
]


# ============================================================
# API CALL
# ============================================================

def ask_agent(message: str, session_id: str) -> str:
    payload = json.dumps(
        {
            "message": message,
            "session_id": session_id,
        }
    ).encode("utf-8")

    request = Request(
        CHAT_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["answer"]

    except HTTPError as exc:
        print(f"\nHTTP ERROR: {exc.code}")
        print(exc.read().decode("utf-8"))
        raise

    except URLError as exc:
        print("\nCould not connect to FastAPI.")
        print(f"Make sure the server is running at {CHAT_URL}")
        print(exc)
        raise


# ============================================================
# BASIC ASSERTIONS
# ============================================================

def check_response(case, answer):
    expect = case.get("expect", {})

    errors = []

    answer_lower = answer.lower()

    # --------------------------------------------------------
    # must_include
    # --------------------------------------------------------

    for phrase in expect.get("must_include", []):
        if phrase.lower() not in answer_lower:
            errors.append(
                f"Missing required text: {phrase}"
            )

    # --------------------------------------------------------
    # must_include_concepts
    #
    # These are behavior-level expectations, so we only print
    # them for manual review rather than pretending exact
    # semantic evaluation is possible here.
    # --------------------------------------------------------

    concepts = expect.get("must_include_concepts", [])

    if concepts:
        print("\nExpected concepts for manual review:")
        for concept in concepts:
            print(f"  - {concept}")

    # --------------------------------------------------------
    # must_not_include
    # --------------------------------------------------------

    for phrase in expect.get("must_not_include", []):
        if phrase.lower() in answer_lower:
            errors.append(
                f"Forbidden text found: {phrase}"
            )

    # --------------------------------------------------------
    # must_not_invent
    # --------------------------------------------------------

    for phrase in expect.get("must_not_invent", []):
        if phrase.lower() in answer_lower:
            errors.append(
                f"Potentially invented information found: {phrase}"
            )

    # --------------------------------------------------------
    # must_not_follow
    # --------------------------------------------------------

    for phrase in expect.get("must_not_follow", []):
        if phrase.lower() in answer_lower:
            errors.append(
                f"Prompt-security violation candidate: {phrase}"
            )

    # --------------------------------------------------------
    # must_not_silently_choose_one
    # --------------------------------------------------------

    if expect.get("must_not_silently_choose_one"):
        print(
            "\nIMPORTANT: Manually verify that the response "
            "acknowledges the source conflict."
        )

    return errors


# ============================================================
# RUN ONE CASE
# ============================================================

def run_case(case, number, total):
    case_id = case["id"]

    # IMPORTANT:
    # Every message in the same case gets the same session ID.
    session_id = f"eval-{case_id}-{uuid.uuid4().hex[:8]}"

    print("\n")
    print("=" * 80)
    print(f"CASE {number}/{total}: {case_id}")
    print(f"Session: {session_id}")
    print("=" * 80)

    final_answer = ""

    for message_number, message in enumerate(
        case["messages"],
        start=1,
    ):
        content = message["content"]

        print("\n" + "-" * 80)
        print(f"Message {message_number}")
        print(f"User: {content}")
        print("-" * 80)

        final_answer = ask_agent(
            message=content,
            session_id=session_id,
        )

        print("\nAssistant:")
        print(final_answer)

    # Only official cases have assertions.
    errors = check_response(
        case,
        final_answer,
    )

    if errors:
        print("\nRESULT: FAIL")

        for error in errors:
            print(f"  - {error}")

        return False

    print("\nRESULT: PASS / MANUAL REVIEW")

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    if not CASES_FILE.exists():
        print(
            f"Could not find {CASES_FILE}. "
            "Place visible-cases(1).json in the project root."
        )
        sys.exit(1)

    with CASES_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    official_cases = data["cases"]

    all_cases = official_cases + ADDITIONAL_CASES

    print("=" * 80)
    print("ASTER & ROW SUPPORT AGENT EVALUATION")
    print("=" * 80)
    print(f"Official cases:   {len(official_cases)}")
    print(f"Additional cases: {len(ADDITIONAL_CASES)}")
    print(f"Total cases:      {len(all_cases)}")
    print("=" * 80)

    passed = 0
    failed = 0

    for number, case in enumerate(
        all_cases,
        start=1,
    ):
        try:
            result = run_case(
                case,
                number,
                len(all_cases),
            )

            if result:
                passed += 1
            else:
                failed += 1

        except Exception as exc:
            failed += 1

            print("\nRESULT: ERROR")
            print(f"  {type(exc).__name__}: {exc}")

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n")
    print("=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    print(f"Total:  {len(all_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    print("=" * 80)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()