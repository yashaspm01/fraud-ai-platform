import json
import re
import requests

from agents.tools import TOOLS, call_tool

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3.2"
MAX_STEPS = 6  # loop protection — per PRD Reliability Architecture


def build_tools_description() -> str:
    lines = []
    for tool in TOOLS:
        params = ", ".join(f"{k} ({v})" for k, v in tool["parameters"].items())
        lines.append(f"- {tool['name']}: {tool['description']} Parameters: {params}")
    return "\n".join(lines)


def build_prompt(goal: str, history: list) -> str:
    tools_desc = build_tools_description()

    history_text = ""
    for step in history:
        history_text += f"Thought: {step['thought']}\n"
        history_text += f"Action: {step['action']}\n"
        history_text += f"Action Input: {json.dumps(step['action_input'])}\n"
        history_text += f"Observation: {json.dumps(step['observation'])}\n"

    return f"""You are a fraud investigation assistant. You have access to these tools:

{tools_desc}

Goal: {goal}

{history_text}
Before deciding your next action, explicitly consider what the most recent
Observation actually told you, and whether you already have enough
information to finish. Do not repeat an action you've already taken with the
same inputs — use the result you already have instead.

Respond in EXACTLY this format for your next step:

Thought: <your reasoning, explicitly referencing relevant observations above>
Action: <tool_name, or "finish" if you have enough information>
Action Input: <a JSON object with the required parameters, or {{"summary": "..."}} if Action is "finish">

Only output one Thought/Action/Action Input block."""

def parse_response(text: str):
    thought_match = re.search(r"Thought:\s*(.+)", text)
    action_match = re.search(r"Action:\s*(.+)", text)
    input_match = re.search(r"Action Input:\s*(\{.*\})", text, re.DOTALL)

    thought = thought_match.group(1).strip() if thought_match else ""
    action = action_match.group(1).strip() if action_match else ""

    try:
        action_input = json.loads(input_match.group(1)) if input_match else {}
    except json.JSONDecodeError:
        action_input = {}

    return thought, action, action_input


def run_agent(goal: str):
    history = []
    seen_actions = set()
    duplicate_count = 0

    for step_num in range(MAX_STEPS):
        prompt = build_prompt(goal, history)
        if duplicate_count >= 1:
            prompt += "\n\nIMPORTANT: You have already tried this exact question and it failed. You now have enough information to finish. Your next Action MUST be 'finish'."

        response = requests.post(OLLAMA_GENERATE_URL, json={"model": LLM_MODEL, "prompt": prompt, "stream": False})
        response.raise_for_status()
        raw_text = response.json()["response"]
        print(f"\n[RAW LLM OUTPUT]\n{raw_text}\n[END RAW]\n")

        thought, action, action_input = parse_response(raw_text)
        action_signature = (action, json.dumps(action_input, sort_keys=True))

        if action.lower() == "finish":
            summary = action_input.get("summary") or thought or "No summary provided."
            print(f"\n✅ FINAL: {summary}")
            return summary, history

        if action_signature in seen_actions:
            duplicate_count += 1
            observation = {"error": "Duplicate action blocked. You MUST finish now with the information you already have."}
        else:
            seen_actions.add(action_signature)
            try:
                observation = call_tool(action, action_input)
            except Exception as e:
                observation = {"error": str(e)}

        print(f"\n--- Step {step_num + 1} ---\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}")
        history.append({"thought": thought, "action": action, "action_input": action_input, "observation": observation})

    print("\n⚠️ Max steps reached without a final answer.")
    return None, history

if __name__ == "__main__":
    goal = "Investigate this transaction: amount=8000, sender_balance_before=8000, sender_balance_after=0, hour_of_day=2. Is this risky, and what does policy say about handling high-risk transactions?"
    run_agent(goal)
