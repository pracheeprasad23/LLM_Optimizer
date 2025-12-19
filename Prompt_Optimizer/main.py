from optimizer.optimizer import optimize_prompt
import json

if __name__ == "__main__":
    user_prompt = input("Enter your prompt:\n> ")

    result = optimize_prompt(user_prompt)

    print(json.dumps(result))