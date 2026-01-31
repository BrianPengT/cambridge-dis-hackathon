import os
import argparse
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# =========================================================
# 1. SETUP
# =========================================================
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "data/Celestia.csv"
MODEL = "gpt-4.1"
TEMPERATURE = 0.2


# =========================================================
# 2. PROMPTS (BY PHASE)
# =========================================================

# ---------- Phase 1: Grounding ----------
GROUNDING_PROMPT = """
You are a NEUTRAL GROUNDER.

Task:
Normalize the Internal Truth and External Claim.

Instructions:
- Break each into atomic propositions.
- Clarify numerical ranges, uncertainty, and scope.
- Do NOT judge faithfulness.
- Do NOT argue.

Output Format:
Truth_Atoms:
- ...

Claim_Atoms:
- ...

Notes:
- ...
"""

# ---------- Phase 2: Logical Implication ----------
FORWARD_ENTAILMENT_PROMPT = """
You are a LOGICAL ANALYST.

Task:
Assess whether the Internal Truth logically implies the External Claim.

Instructions:
- Assume the Truth is fully accurate.
- Determine whether the Claim must be true.
- Identify assumptions or narrow edge cases where the implication holds.

Output Format:
Assessment:
- Entailed / Partially Entailed / Not Entailed

Edge_Cases:
- ...
"""

REVERSE_ENTAILMENT_PROMPT = """
You are a LOGICAL ANALYST.

Task:
Assess whether the External Claim implies the Internal Truth.

Instructions:
- Assume the Claim is true.
- Determine whether the Truth must also be true.
- Identify alternative scenarios where the Claim holds but the Truth does not.

Output Format:
Assessment:
- Entailed / Partially Entailed / Not Entailed

Counterexamples:
- ...
"""

# ---------- Phase 3: Perspective Expansion ----------
OPTIMIST_PROMPT = """
You are the OPTIMIST (Charitable Interpreter).

Goal:
Give the strongest reasonable case that the External Claim faithfully
represents the Internal Truth.

Guidelines:
- Assume good faith and shared context.
- Treat omissions as simplifications unless critical.
- Highlight compatible interpretations.

Output:
Argument:
- ...
Edge_Cases:
- ...
"""

PESSIMIST_PROMPT = """
You are the PESSIMIST (Skeptical Interpreter).

Goal:
Give the strongest reasonable case that the External Claim is misleading
or mutated relative to the Internal Truth.

Guidelines:
- Assume a critical audience.
- Highlight omissions, reframing, and audience impact.
- Focus on how the claim could mislead even if technically compatible.

Output:
Argument:
- ...
Edge_Cases:
- ...
"""

# ---------- Phase 4: Controlled Interaction ----------
ASSUMPTION_CHALLENGER_PROMPT = """
You are an ASSUMPTION CHALLENGER.

Inputs include:
- Logical entailment analyses
- Optimist and Pessimist perspectives

Task:
- Identify key assumptions required for each interpretation.
- Identify where the perspectives diverge.
- Do NOT argue for a side.

Output Format:
Key_Assumptions:
- Faithful_if:
  - ...
- Misleading_if:
  - ...

Tension_Points:
- ...
"""

# ---------- Phase 5: Counterfactual Loop ----------
COUNTERFACTUAL_PROMPT = """
You are a COUNTERFACTUAL TESTER.

Task:
Stress-test the relationship between the Truth and the Claim.

Questions:
1. Can the Claim be true while the Truth is false?
2. Can the Truth be true while the Claim is misleading?

Output Format:
Counterfactual_Scenarios:
- Scenario_1:
  - ...
- Scenario_2:
  - ...

Audience_Risks:
- ...
"""

# ---------- Phase 6: Synthesis ----------
SYNTHESIZER_PROMPT = """
You are a SYNTHESIZER.

Inputs include:
- Grounded propositions
- Entailment analyses
- Perspective arguments
- Assumption and counterfactual analyses

Task:
- You must output a final decision and a transparent reason why.
- Map all reasonable interpretations.
- Explain what drives disagreement.

Output Format: 
Interpretive_Map:
- Perspective_A:
  - Description:
  - Required_Assumptions:
  - Risks:

- Perspective_B:
  - Description:
  - Required_Assumptions:
  - Risks:

Summary:
- Core sources of ambiguity or disagreement.
"""


# =========================================================
# 3. HELPER FUNCTION
# =========================================================
def run_agent(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
    )
    return response.choices[0].message.content.strip()


# =========================================================
# 4. MAIN LOOP (PHASED)
# =========================================================
def test_row(row_index):
    df = pd.read_csv(INPUT_FILE)
    row = df.iloc[row_index]

    truth = row.get("truth", "N/A")
    claim = row.get("claim", "N/A")

    base_input = f"""
INTERNAL TRUTH:
{truth}

EXTERNAL CLAIM:
{claim}
"""

    print("\n" + "=" * 80)
    print(f"TESTING ROW {row_index}")
    print("=" * 80)

    # ---------- Phase 1 ----------
    grounding = run_agent(GROUNDING_PROMPT, base_input)
    print("\n[PHASE 1: GROUNDING]\n", grounding)

    # ---------- Phase 2 ----------
    forward = run_agent(FORWARD_ENTAILMENT_PROMPT, base_input)
    reverse = run_agent(REVERSE_ENTAILMENT_PROMPT, base_input)
    print("\n[PHASE 2: FORWARD ENTAILMENT]\n", forward)
    print("\n[PHASE 2: REVERSE ENTAILMENT]\n", reverse)

    # ---------- Phase 3 ----------
    optimist = run_agent(OPTIMIST_PROMPT, base_input)
    pessimist = run_agent(PESSIMIST_PROMPT, base_input)
    print("\n[PHASE 3: OPTIMIST]\n", optimist)
    print("\n[PHASE 3: PESSIMIST]\n", pessimist)

    # ---------- Phase 4 ----------
    assumption_input = f"""
GROUNDING:
{grounding}

FORWARD ENTAILMENT:
{forward}

REVERSE ENTAILMENT:
{reverse}

OPTIMIST:
{optimist}

PESSIMIST:
{pessimist}
"""
    assumptions = run_agent(ASSUMPTION_CHALLENGER_PROMPT, assumption_input)
    print("\n[PHASE 4: ASSUMPTION CHALLENGER]\n", assumptions)

    # ---------- Phase 5 ----------
    counterfactuals = run_agent(COUNTERFACTUAL_PROMPT, base_input)
    print("\n[PHASE 5: COUNTERFACTUALS]\n", counterfactuals)

    # ---------- Phase 6 ----------
    synthesis_input = f"""
GROUNDING:
{grounding}

ENTAILMENT:
{forward}
{reverse}

PERSPECTIVES:
{optimist}
{pessimist}

ASSUMPTIONS:
{assumptions}

COUNTERFACTUALS:
{counterfactuals}
"""
    synthesis = run_agent(SYNTHESIZER_PROMPT, synthesis_input)
    print("\n[PHASE 6: SYNTHESIS]\n", synthesis)

    print("\n" + "=" * 80 + "\n")


# =========================================================
# 5. CLI ENTRY
# =========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multi-agent interpretive loop.")
    parser.add_argument("row", type=int, nargs="?", default=0)
    args = parser.parse_args()

    test_row(args.row)
