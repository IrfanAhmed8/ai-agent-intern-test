from app.agent.agent import SupportAgent


def main():

    agent = SupportAgent()

    context = """
Source: 01-returns-policy-current.md
Heading: Standard return window

Customers on the standard plan may request a return
within 30 calendar days of delivery.
"""

    answer = agent.answer(
        user_message="How long do I have to return an unused backpack?",
        context=context,
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()