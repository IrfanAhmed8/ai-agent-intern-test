from app.agent.agent import SupportAgent


def main():

    agent = SupportAgent()

    answer = agent.answer(
        "Can I put the entire Breeze Tumbler in the dishwasher?"
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()