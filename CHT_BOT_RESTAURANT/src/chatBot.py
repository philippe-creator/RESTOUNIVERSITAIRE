from agent import create_agent_instance


def main():

    agent = create_agent_instance()

    print("Chatbot prêt. Tape 'quit' pour quitter.")

    while True:

        question = input("\nVous : ")

        if question.lower() == "quit":
            break

        response = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )

        print("\nBot :", response["messages"][-1].content)


if __name__ == "__main__":
    main()