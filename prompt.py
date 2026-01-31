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

MATH_ABSTRACTOR_FACT = """
You are a Math abstractor.
Extract the methematical message from internal fact only.
Focus on quantities, relationships, and operations.
Ignore rhetoric and intent.
Provide a concise summary of the mathematical content.

Output:
- Title: Short descriptive title
- Math Summary: Concise summary of mathematical content
- Reason: literal and precise
"""

MATH_ABSTRACTOR_CLAIM = """
You are a Math abstractor.
Extract the methematical message from claim only.
Focus on quantities, relationships, and operations.
Ignore rhetoric and intent.
Provide a concise summary of the mathematical content.

Output:
- Title: Short descriptive title
- Math Summary: Concise summary of mathematical content
- Reason: literal and precise
"""

SKEPTIC_PROMPT = """
You are a Skeptic.
Assume the external claim is misleading unless proven otherwise.
Focus on meaning shift, exaggeration, or missing context.
Consistency between fact and claim is not enough. Check that they are equivalent.

Output:
- Verdict: Faithful / Mutated
- Reason: 2–4 sentences
"""

FACTCHECKER_PROMPT = """
You are a Pedantic Fact-Checker.
Judge whether the external claim is technically supported
by the internal fact. Ignore intent and rhetoric.
Consistency between fact and claim is not enough. Check that they are equivalent.

Output:
- Verdict: Faithful / Mutated
- Reason: literal and precise
"""

COMMONSENSE_PROMPT = """
You are a Common Sense Judge.
Decide whether a reasonable reader would be misled.

Output:
- Verdict: Faithful / Mutated
- Reason: plain language explanation
"""


def debate(internal_fact: str, external_claim: str, model: str = "gpt-4.1-mini") -> None:
    case = f"""
    INTERNAL FACT:
    {internal_fact}

    EXTERNAL CLAIM:
    {external_claim}

    """


    # start answer
    mathabstractor = run_agent(model, MATH_ABSTRACTOR_PROMPT, case)
        
    print("=== Math Abstractor ===")
    print(mathabstractor)
    
    case += f"\nMATH ABSTRACTOR:\n{mathabstractor}\n"
    
    skeptic = run_agent(model, SKEPTIC_PROMPT, case)
    factchecker = run_agent(model, FACTCHECKER_PROMPT, case)
    commonsense = run_agent(model, COMMONSENSE_PROMPT, case)


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

    MATH ABSTRACTOR:
    {mathabstractor}

    SKEPTIC:
    {skeptic}

    FACT-CHECKER:
    {factchecker}

    COMMON-SENSE:
    {commonsense}
    """

    verdict = run_agent(model, JURY_PROMPT, jury_input)

    print("\n=== FINAL VERDICT ===")
    print(verdict)
