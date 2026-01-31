import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Change model if needed (e.g., "gpt-4o", "gpt-3.5-turbo")
MODEL = "gpt-4.1" 

INPUT_FILE = "data/Celestia.csv"
OUTPUT_FILE = "results/Celestia_Verdict.csv"

# --- 2. PROMPTS ---

OPTIMIST_PROMPT = """
You are the OPTIMIST (The Proponent). 
Your goal is to argue that the External Claim is FAITHFUL to the Internal Fact.
- Interpret the claim charitably.
- Highlight logical connections and reasonable inferences.
- Downplay minor omissions as necessary simplification.
- Assume the author had good intent.

Output:
- Argument: A persuasive paragraph explaining why this is accurate.
"""

PESSIMIST_PROMPT = """
You are the PESSIMIST (The Critic). 
Your goal is to argue that the External Claim is MUTATED or misleading.
- Interpret the claim strictly and literally.
- Highlight exaggeration, missing context, or specific details that were lost.
- Point out where the claim implies more than the evidence supports.
- Assume the author is trying to manipulate the reader.

Output:
- Argument: A sharp paragraph explaining why this is misleading.
"""

JUDGE_PROMPT = """
You are the IMPARTIAL JUDGE.
You have been presented with a Fact, a Claim, and two opposing arguments (Optimist vs Pessimist).
Your task is to deliver a final verdict on whether the Claim is FAITHFUL or MUTATED.

Rules:
1. Weigh the arguments. Does the Pessimist identify a critical flaw, or is the Optimist right that the meaning is preserved?
2. You must pick a side.
3. Provide a clear justification.

Output Format:
Verdict: [FAITHFUL / MUTATED]
Reasoning: [2-3 sentences explaining your decision]
"""

# --- 3. HELPER FUNCTIONS ---

def run_agent(model, system_prompt, user_prompt):
    """Sends a prompt to OpenAI and returns the text response."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2, 
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API Error: {e}")
        return "Error"

# --- 4. MAIN EXECUTION ---

def process_debate():
    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File '{INPUT_FILE}' not found.")
        return

    # Load data
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} rows from {INPUT_FILE}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # --- CHANGE: Checking for 'truth' and 'claim' columns ---
    required_cols = ['truth', 'claim']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV is missing columns. Found: {df.columns}")
        print(f"Expected columns: {required_cols}")
        return

    # Storage for results
    optimist_args = []
    pessimist_args = []
    judgments = []

    # Loop through each row in the CSV
    for index, row in df.iterrows():
        # --- CHANGE: Mapping your specific column names ---
        internal_fact = row['truth']
        external_claim = row['claim']
        
        # Prepare the case text
        case_input = f"INTERNAL FACT (TRUTH):\n{internal_fact}\n\nEXTERNAL CLAIM:\n{external_claim}"

        print(f"\n--- Processing Row {index + 1}/{len(df)} ---")

        # 1. Run Optimist
        print("  > Consulting Optimist...")
        optimist_out = run_agent(MODEL, OPTIMIST_PROMPT, case_input)
        optimist_args.append(optimist_out)

        # 2. Run Pessimist
        print("  > Consulting Pessimist...")
        pessimist_out = run_agent(MODEL, PESSIMIST_PROMPT, case_input)
        pessimist_args.append(pessimist_out)

        # 3. Run Judge
        print("  > Judge is deliberating...")
        judge_input = f"""
        CASE:
        {case_input}

        OPTIMIST ARGUMENT:
        {optimist_out}

        PESSIMIST ARGUMENT:
        {pessimist_out}
        """
        verdict_out = run_agent(MODEL, JUDGE_PROMPT, judge_input)
        judgments.append(verdict_out)
        
        # Print just the first line (Verdict) for cleaner terminal output
        print(f"  > Verdict: {verdict_out.splitlines()[0]}") 

    # Save results
    df['Optimist_View'] = optimist_args
    df['Pessimist_View'] = pessimist_args
    df['Judge_Verdict'] = judgments

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSuccess! Results saved to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    process_debate()