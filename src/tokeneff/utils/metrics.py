from tokeneff.utils.tokenizer_utils import count_tokens

def token_savings(original: str, optimized: str, model: str = "gpt-4o-mini") -> float:
    """Calculate token savings percentage"""
    orig_tokens = count_tokens(original, model)
    opt_tokens = count_tokens(optimized, model)

    return 100 * (1 - opt_tokens / orig_tokens)