import mcp_client
import requests
import json
import mcp_client
import asyncio


url = "http://192.168.8.172:11434/api/generate"

SYSTEM_PROMPT = """
You are a decision engine.

You MUST respond with ONLY valid JSON.
No explanations. No text outside JSON.

You have access to ONE tool:

Tool name: add_numbers
Arguments:
- a: integer
- b: integer

Rules:
- If the user explicitly asks to add numbers, CALL THE TOOL.
- If the question can be answered directly, return an answer.
- Never do math yourself if calling the tool is appropriate.

Allowed response formats ONLY:

Answer:
{
  "type": "answer",
  "result": number
}

Tool call:
{
  "type": "tool_call",
  "tool": "add_numbers",
  "arguments": {
    "a": number,
    "b": number
  }
}
"""

user_input = "Add 2 and 3"

payload = {
    "model": "qwen2.5:1.5b",
    "prompt": SYSTEM_PROMPT + "\nUser: " + user_input,
    "stream": False
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    data = response.json()
    response_text = data["response"]
    response_json = json.loads(response_text)
    if response_json["type"] == "answer":
        print("Answer:")
        print(response_json["result"])
    elif response_json["type"] == "tool_call":
        print("Tool call:")
        print(response_json["tool"])
        arguments = response_json["arguments"]
        if response_json["tool"] == "add_numbers":
            result = asyncio.run(mcp_client.call_mcp_tool("add_numbers", arguments))
            print("Result:")
            print(result)
            followup_prompt = f"""
The tool '{response_json["tool"]}' was executed successfully.

Tool result:
{{
  "result": {result}
}}

Now return the final answer to the user.
Respond ONLY in JSON format:

{{
  "final_answer": number
}}
"""
            print("Followup prompt:")
            print(followup_prompt)

            payload = {
                "model": "qwen2.5:1.5b",
                "prompt": followup_prompt,
                "stream": False
            }

            followup_response = requests.post(url, data=json.dumps(payload), headers=headers)

            if followup_response.status_code == 200:
                data = followup_response.json()
                response_text = data["response"]
                response_json = json.loads(response_text)
                final_raw = followup_response.json()["response"]

                print("\nFinal model response:")
                print(final_raw)

                final_data = json.loads(final_raw)
                print("\nParsed final answer:")
                print(final_data)


else:
    print(f"Error: {response.status_code}")

