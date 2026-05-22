import re

def classify_intent(prompt: str):
    """Predicts prompt intent, complexity, expected output, latency tolerance, and compliance."""
    p_lower = prompt.lower()

    # Intent Type
    if any(x in p_lower for x in ["why", "analyze", "explain", "reason", "derive", "justify"]):
        intent = "reasoning"
    elif any(x in p_lower for x in ["summarize", "in short", "briefly"]):
        intent = "summarization"
    elif any(x in p_lower for x in ["code", "program", "function", "python", "java", "c++", "algorithm"]):
        intent = "coding"
    elif any(x in p_lower for x in ["dataset", "analyze data", "plot", "visualize", "csv"]):
        intent = "data_analysis"
    elif any(x in p_lower for x in ["story", "poem", "creative", "write about"]):
        intent = "creative_writing"
    elif any(x in p_lower for x in ["who", "what", "when", "where", "fact", "define"]):
        intent = "factual_answering"
    elif any(x in p_lower for x in ["conversation", "chat", "talk", "discuss"]):
        intent = "conversation"
    elif any(x in p_lower for x in ["classify", "category", "type of", "label"]):
        intent = "classification"
    else:
        intent = "other"

    # Complexity Level
    word_count = len(p_lower.split())
    if word_count < 10:
        complexity = "low"
    elif word_count < 30:
        complexity = "medium"
    else:
        complexity = "high"

    # Expected Output Length
    if any(x in p_lower for x in ["short", "summary", "brief"]):
        output_len = "short"
    elif any(x in p_lower for x in ["explain", "detailed", "step", "comprehensive", "in depth"]):
        output_len = "long"
    else:
        output_len = "medium"

    # Latency Tolerance (reverse of expected output)
    latency_map = {"short": "low", "medium": "medium", "long": "high"}
    latency = latency_map[output_len]

    # Compliance Need
    compliance = any(x in p_lower for x in [
        "personal data", "pii", "privacy", "gdpr", "confidential", "sensitive", "policy", "terms"
    ])

    return {
        "intent_type": intent,
        "complexity_level": complexity,
        "expected_output_length": output_len,
        "latency_tolerance": latency,
        "compliance_needed": compliance
    }