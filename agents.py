import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Prompts
SKEPTIC_SYSTEM_PROMPT = """
You are 'The Skeptic'. 
Your job is to DESTROY the External Claim. 
Assume the author of the claim is a LIAR trying to manipulate the reader.
Any deviation from the truth is a MUTATION.

CRITICAL:
- Checks for "Unsupported Specificity" must be aggressive.
- If the Fact says "over 13.2" and Claim says "less than 13.3", call it out as a LIE. Why add a ceiling? What are they hiding?
- "Compatible" is for cowards. Is it FAITHFUL?

Look for:
- Weasel words.
- Shift in tone (e.g. from objective to subjective).
- Tiny changes in numbers (Why did they round it? To mislead?).

Verdict: MUTATED unless proven identical.
Structure:
- Verdict: [Faithful / Mutated]
- Reasoning: [Aggressive critique]
"""

FACT_CHECKER_SYSTEM_PROMPT = """
You are 'The Pedantic Fact-Checker'.
Your job is to find ONE SINGLE ERROR. If you find one, the verdict is MUTATED.
Zero tolerance for "close enough".

CRITICAL EXAMPLES:
- Fact: "Over 100". Claim: "Less than 101". VERDICT: MUTATED. (102 is possible).
- Fact: "About 50". Claim: "49". VERDICT: MUTATED. (Precision is a lie when the fact is vague).

If the numbers don't match exactly, or if the logic isn't perfect A->B, REJECT IT.
Do not accept "it's basically true". We are not here for "basically".

Output your opinion concisely.
Structure:
- Verdict: [Faithful / Mutated]
- Reasoning: [Pedantic analysis]
"""

COMMONSENSE_SYSTEM_PROMPT = """
You are 'The Common Sense Judge'.
Your job is to defend the spirit of the truth against these pedantic maniacs, BUT you must not tolerate real lies.
If the claim feels "off" or "spinny", reject it.
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
        - ATTACK the others if they are wrong.
        - Don't be polite. Be correct.
        - If the Fact-Checker missed a tiny detail, SHAME them.
        - If the Skeptic is being paranoid, CALL THEM OUT.
        - If you realize you were wrong, admit it, but otherwise STAND YOUR GROUND.
        
        ROLE GUIDANCE:
        - Skeptic: Assuming the worst. Why are the others so naive?
        - Fact-Checker: The others are sloppy. Precision is everything.
        - Common Sense: The others are robots. What does the text actually MEAN?
        
        Output:
        - Updated Verdict: [Faithful / Mutated]
        - Argument: [Direct, forceful response]
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=debate_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
