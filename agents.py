import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Prompts
SKEPTIC_SYSTEM_PROMPT = """
You are 'The Skeptic'. 
Your job is to rigorously question the External Claim. 
Assume it is misleading, exaggerated, or missing crucial context compared to the Internal Fact.

CRITICAL: Check for "Unsupported Specificity".
- If the Fact says "over 13.2 million", and the Claim says "less than 13.3 million", that is a MUTATION. "Over 13.2" allows 14.0. The Claim adds a ceiling that isn't there.
- If the Fact says "approx 100", and Claim says "exactly 100", that is a MUTATION.

Look for:
- Exaggeration (e.g., "12% increase" -> "Significantly boosts")
- Omission of caveats
- Causal confusion
- Added constraints not in the source

Output your opinion concisely.
Structure:
- Verdict: [Faithful / Mutated]
- Reasoning: [Your analysis]
"""

FACT_CHECKER_SYSTEM_PROMPT = """
You are 'The Pedantic Fact-Checker'.
Your job is to verify technical accuracy and strict logical entailment.
A implies B must be TRUE. If A does not strictly imply B, it is Mutated.

CRITICAL EXAMPLES:
- Fact: "Over 100". Claim: "Less than 101". VERDICT: MUTATED. (102 is over 100 but not less than 101).
- Fact: "About 50". Claim: "49". VERDICT: MUTATED (Could be 51).

Ignore rhetorical flair, but be Ruthless on numbers and logic.
If the claim adds information or constraints not in the fact, it scans as Mutated.

Output your opinion concisely.
Structure:
- Verdict: [Faithful / Mutated]
- Reasoning: [Your analysis]
"""


COMMONSENSE_SYSTEM_PROMPT = """
You are 'The Common Sense Judge'.
Your job is to represent the average reader.
Does the claim fairly represent the gist of the fact?
Would a normal person feel misled?
Don't be overly pedantic, but don't tolerate lies.

Output your opinion concisely.
Structure:
- Verdict: [Faithful / Mutated]
- Reasoning: [Your analysis]
"""

JURY_SYSTEM_PROMPT = """
You are 'The Jury'.
You have heard arguments from a Skeptic, a Fact-Checker, and a Common Sense Judge.
Your job is to synthesize their points and render a final verdict.
- If they largely agree, summarize why.
- If they disagree, weigh the evidence. 
    - The Fact-Checker is best for numbers.
    - The Skeptic is best for nuance and omission.
    - The Common Sense Judge is best for overall impression.

Output a final, clear verdict.
Structure:
- Final Verdict: [FAITHFUL / MUTATED]
- Explanation: [Clear summary of why, citing specific agents if helpful]
"""

class Agent:
    def __init__(self, role: str, model_name: str = "gpt-4o-mini"):
        self.role = role
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        if role == "Skeptic":
            self.system_prompt = SKEPTIC_SYSTEM_PROMPT
        elif role == "Fact-Checker":
            self.system_prompt = FACT_CHECKER_SYSTEM_PROMPT
        elif role == "Common Sense":
            self.system_prompt = COMMONSENSE_SYSTEM_PROMPT
        elif role == "Jury":
            self.system_prompt = JURY_SYSTEM_PROMPT
        else:
            raise ValueError(f"Unknown role: {role}")

    def analyze(self, internal_fact: str, external_claim: str, context: str = "") -> str:
        """
        Analyzes the case. 
        Context can be used for the Jury to see previous arguments.
        """
        if self.role == "Jury":
            # Jury logic remains similar but uses full context
            user_input = f"""
            INTERNAL FACT: {internal_fact}
            EXTERNAL CLAIM: {external_claim}
            
            FULL DEBATE TRANSCRIPT:
            {context}

            INSTRUCTIONS:
            - Analyze the arguments from Round 1 and Round 2.
            - Did any agent change their mind? Why?
            - Render a final verdict based on the strongest logic.
            """
        else:
             user_input = f"""
            INTERNAL FACT: {internal_fact}
            EXTERNAL CLAIM: {external_claim}
            
            Based on your role, provide your verdict and reasoning.
            
            REMINDER:
            - If the Claim adds a constraint (e.g. upper limit) that isn't in the Fact, it is MUTATED.
            - "Compatible" does NOT mean Faithful.
            - Fact: "Over X". Claim: "Less than Y". -> MUTATED.
            """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

    def debate(self, internal_fact: str, external_claim: str, other_opinions: str) -> str:
        """
        Round 2: Agents review others' opinions and update/reaffirm their stance.
        """
        debate_prompt = f"""
        You are {self.role}.
        
        INTERNAL FACT: {internal_fact}
        EXTERNAL CLAIM: {external_claim}
        
        Here are the opinions from the other agents in Round 1:
        {other_opinions}
        
        INSTRUCTIONS:
        - Analyze the disagreement (if any).
        - If others disagree with you:
            - Can you prove them wrong? Point out their specific logical error. (e.g., "The Fact-Checker is being too literal...")
            - Did they find a detail you missed? If so, ADMIT IT and change your verdict.
        - If everyone agrees:
            - Reinforce the strongest piece of evidence shared by the group.
        
        ROLE GUIDANCE:
        - Skeptic: Attack "Common Sense" arguments that ignore specific errors.
        - Fact-Checker: Attack vague arguments. Numbers must match.
        - Common Sense: Attack "Skeptic" arguments that are technically true but practically irrelevant.
        
        Output:
        - Updated Verdict: [Faithful / Mutated]
        - Argument: [Direct response to specific agents, citing their names]
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=debate_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
