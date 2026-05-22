import tiktoken

def count_tokens(prompt: str, model_name="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(prompt))