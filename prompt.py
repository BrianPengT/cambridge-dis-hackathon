import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def run_agent(model, system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

MATH_ABSTRACTOR_FACT_PROMPT = """
You are a Math abstractor.
Extract the methematical message from internal fact only. Ignore the external claim.
Focus on quantities, relationships, and operations.
Ignore rhetoric and intent.
Provide a concise summary of the mathematical content and its precision. For open bounds, use the precision given to suggest its possible range of values on the other side.

Output:
- Title: Short descriptive title
- Math Summary: Concise summary of mathematical content
- Reason: literal and precise
"""

MATH_ABSTRACTOR_CLAIM_PROMPT = """
You are a Math abstractor.
Extract the methematical message from external claim only. Ignore the internal fact.
Focus on quantities, relationships, and operations.
Ignore rhetoric and intent.
Provide a concise summary of the mathematical content and its precision. For open bounds, use the precision given to suggest its possible range of values on the other side.

Output:
- Title: Short descriptive title
- Math Summary: Concise summary of mathematical content
- Reason: literal and precise
"""

# MATH_CHECKER_PROMPT = """
# You are a Math Checker.
# Compare the mathematical summaries from internal fact and external claim.
# Identify discrepancies in quantities, relationships, or operations.
# It's not enough to say they are consistent. Check for equivalence.

# Output:
# - Verdict: Faithful / Mutated
# - Reason: 2–4 sentences
# """

SKEPTIC_PROMPT = """
You are a Skeptic.
Assume the external claim is not equivalent with the internal fact unless proven otherwise.
Focus on meaning shift, exaggeration, or missing context.
Just give reasons for mutation. Provide concrete examples.
Consistency between fact and claim is not enough. Check that they are equivalent.


Output:
- Reason: 2–4 sentences
"""

FACTCHECKER_PROMPT = """
You are a Pedantic Fact-Checker. Check that if the fact technically implies the claim in all possible circumstances. Focus on information that the external claim adds to the internal fact.
Ignore intent and rhetoric.

Output:
- Verdict: Faithful / Mutated
- Reason: literal and precise
"""

COMMONSENSE_PROMPT = """
You are a Common Sense Judge.
Decide whether a reasonable reader would be misled. Even if the fact technically implies the claim, would it still feel result in a misleading impression?
For mathematical claims that are open lower or upper bounds, consider practical implications based on their precisions.

For example, if a claim states "at least 30" for a quantity that is actually 1000000, it may mislead readers to underestimate the scale.

Output:
- Verdict: Faithful / Mutated
- Reason: plain language explanation
"""


def debate(internal_fact: str, external_claim: str, model: str = "gpt-4.1-mini") -> None:
    case = f"""
    Here is an internal fact and an external claim to evaluate. The internal fact is the source information that should be taken as truth, and the external claim is a statement written by someone with access to the internal fact.
    
    INTERNAL FACT:
    {internal_fact}

    EXTERNAL CLAIM:
    {external_claim}

    """


    # start answer
    mathabstractor_fact = run_agent(model, MATH_ABSTRACTOR_FACT_PROMPT, case)
    mathabstractor_claim = run_agent(model, MATH_ABSTRACTOR_CLAIM_PROMPT, case)
        
    print("=== Math Abstractor Fact ===")
    print(mathabstractor_fact)
    
    print("\n=== Math Abstractor Claim ===")
    print(mathabstractor_claim)
    
    information = ""
    information += f"\nMATH ABSTRACTOR FACT:\n{mathabstractor_fact}\n"
    information += f"\nMATH ABSTRACTOR CLAIM:\n{mathabstractor_claim}\n"
    
    skeptic = run_agent(model, SKEPTIC_PROMPT, case + information)
    
    information += f"\nSKEPTIC:\n{skeptic}\n"
    factchecker = run_agent(model, FACTCHECKER_PROMPT, case + information)
    
    information += f"\nFACT-CHECKER:\n{factchecker}\n"
    commonsense = run_agent(model, COMMONSENSE_PROMPT, case + information)
    information += f"\nCOMMON-SENSE:\n{commonsense}\n"

    print("\n=== Skeptic ===")
    print(skeptic)

    print("\n=== Fact Checker ===")
    print(factchecker)

    print("\n=== Common Sense ===")
    print(commonsense)


    # jury

    JURY_PROMPT = """
    You are the Jury.
    You must decide whether the external claim is FAITHFUL or MUTATED.

    Rules:
    - Base your decision ONLY on the agents' opinions
    - Explicitly mention disagreements
    - Give a final verdict with justification
    """


    jury_input = f"""
    CASE:
    {case}

    INFORMATION FROM AGENTS:
    {information}
    """

    verdict = run_agent(model, JURY_PROMPT, jury_input)

    print("\n=== FINAL VERDICT ===")
    print(verdict)
