
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
prompt = "Hello"

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



#Agent1
SKEPTIC_PROMPT = """
You are a Skeptic.
Assume the external claim is misleading unless proven otherwise.
Focus on meaning shift, exaggeration, or missing context.

Output:
- Verdict: Faithful / Mutated
- Reason: 2–4 sentences
"""

FACTCHECKER_PROMPT = """
You are a Pedantic Fact-Checker.
Judge whether the external claim is technically supported
by the internal fact. Ignore intent and rhetoric.

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




case = """
INTERNAL FACT:
The study reports a 12% increase in engagement among users aged 18–25.

EXTERNAL CLAIM:
"This feature significantly boosts user engagement."

"""


# start answer

skeptic = run_agent("gpt-4.1", SKEPTIC_PROMPT, case)
factchecker = run_agent("gpt-4.1", FACTCHECKER_PROMPT, case)
commonsense = run_agent("gpt-4.1", COMMONSENSE_PROMPT, case)

print("=== Skeptic ===")
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

SKEPTIC:
{skeptic}

FACT-CHECKER:
{factchecker}

COMMON-SENSE:
{commonsense}
"""

verdict = run_agent("gpt-4.1", JURY_PROMPT, jury_input)

print("\n=== FINAL VERDICT ===")
print(verdict)
