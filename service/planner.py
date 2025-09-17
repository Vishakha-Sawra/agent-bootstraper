import google.genai as genai
import json
from dotenv import load_dotenv
import os

# Load .env file (for GEMINI_API_KEY)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment or .env file")
print("GEMINI_API_KEY loaded successfully:", bool(api_key))

def extract_json(text: str) -> dict:
    """
    Safely extracts the first JSON object from a string, stripping Markdown code fences if present.
    """
    text = text.strip()

    # Remove ```json or ``` at start and ``` at end
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    if not text:
        raise ValueError("Empty response from Gemini after stripping code fences")

    decoder = json.JSONDecoder()
    try:
        obj, idx = decoder.raw_decode(text)
        return obj
    except json.JSONDecodeError as e:
        print("Raw Gemini response causing JSONDecodeError:")
        print(repr(text))
        raise ValueError(f"Failed to decode JSON: {e}")

def generate_plan(scan_summary: dict) -> dict:
    """
    Generates a tailored execution plan from the repository scan.
    Uses scan_summary details (e.g., languages, frameworks, entrypoints) to customize files.
    """
    client = genai.Client()

    # Create a dynamic prompt describing the project details
    prompt = f"""
You are an expert DevOps engineer. Analyze the following repository details:
{json.dumps(scan_summary, indent=2)}

Based on the information above, generate a step-by-step execution plan to build and deploy this project.
For each step, output a JSON object with:
  - "tool": one of "create_dockerfile", "write_docker_compose", "setup_ci_pipeline", "generate_k8s_manifests", or "deploy_to_cluster".
  - "args": an object containing:
      • "file_path": the file path where the tailored configuration should be written.
      • "content": the complete, project-specific content of the file.
      (Additional keys may be included only if needed by deployment steps.)
  - "success_check": a short message confirming the file was generated.
  - Optionally, "on_fail": an error message if the step fails.

Respond with ONLY valid JSON.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print("Raw Gemini response:")
    print(repr(response.text))
    plan_json = extract_json(response.text)
    return plan_json