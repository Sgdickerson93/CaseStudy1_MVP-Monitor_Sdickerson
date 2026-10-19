# Monitor Program

# Authentication to AlphaSense API
import os
import requests
import time
import json
from pathlib import Path


# -------------------------
# Authentication
# -------------------------

api_key = os.environ["ALPHASENSE_API_KEY"]
client_id = os.environ["ALPHASENSE_CLIENT_ID"]
client_secret = os.environ["ALPHASENSE_CLIENT_SECRET"]
email = os.environ["ALPHASENSE_EMAIL"]
password = os.environ["ALPHASENSE_PASSWORD"]

auth_response = requests.post(
    "https://api.alpha-sense.com/auth",
    headers={
        "x-api-key": api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={
        "grant_type": "password",
        "username": email,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret,
    },
)

auth_response.raise_for_status()

access_token = auth_response.json()["access_token"]
print("Authenticated successfully.")


# -------------------------
# Variables / Paths
# -------------------------

GRAPHQL_URL = "https://api.alpha-sense.com/gql"

OUTPUT_FOLDER = Path("reports")
OUTPUT_FOLDER.mkdir(exist_ok=True)

MONITOR_FILE = OUTPUT_FOLDER / "monitor.json"


# -------------------------
# GenSearch
# -------------------------

mutation = """
mutation GenSearch($input: GenSearchInput!) {
  genSearch {
    auto(input: $input) {
      id
    }
  }
}
"""

headers = {
    "x-api-key": api_key,
    "clientid": client_id,
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}


# -------------------------
# New or Existing Monitor
# -------------------------

if MONITOR_FILE.exists():

    # Load the existing monitor
    saved_text = MONITOR_FILE.read_text(encoding="utf-8")
    monitor_data = json.loads(saved_text)

    conversation_id = monitor_data.get("conversation_id")
    research_question = monitor_data.get("research_question")

    print(f"Existing monitor found: {research_question}")

    follow_up_prompt = (
        f"What has changed since the last run regarding: {research_question}"
    )

    variables = {
        "input": {
            "prompt": follow_up_prompt,
            "conversationId": conversation_id,
        }
    }

else:

    # Create a new monitor
    research_question = input("What would you like to monitor? ")

    variables = {
        "input": {
            "prompt": research_question
        }
    }


# -------------------------
# Submit GenSearch
# -------------------------

response = requests.post(
    GRAPHQL_URL,
    headers=headers,
    json={
        "query": mutation,
        "variables": variables,
    },
)

response.raise_for_status()

conversation_id = response.json()["data"]["genSearch"]["auto"]["id"]

print(f"GenSearch started — conversation ID: {conversation_id}")


# -------------------------
# Save Monitor State
# -------------------------

monitor_data = {
    "conversation_id": conversation_id,
    "research_question": research_question,
}

updated_file = json.dumps(monitor_data)

MONITOR_FILE.write_text(
    updated_file,
    encoding="utf-8",
)


# -------------------------
# Poll GenSearch
# -------------------------

poll_query = """
query Query($conversationId: String!) {
  genSearch {
    conversation(id: $conversationId) {
      id
      markdown
      progress
      error {
        code
      }
    }
  }
}
"""

while True:

    poll_response = requests.post(
        GRAPHQL_URL,
        headers=headers,
        json={
            "query": poll_query,
            "variables": {
                "conversationId": conversation_id
            },
        },
    )

    poll_response.raise_for_status()

    conversation = poll_response.json()["data"]["genSearch"]["conversation"]

    progress = conversation["progress"]

    print(f"Progress: {progress:.0%}")

    if conversation.get("error"):
        raise RuntimeError(
            f"GenSearch error: {conversation['error']['code']}"
        )

    if progress >= 1.0:
        break

    time.sleep(2)


# -------------------------
# Save Research Report
# -------------------------

if conversation["markdown"]:

    result_file = input("Enter file name: ")

    OUTPUT_FILE = (
        OUTPUT_FOLDER
        / f"{result_file}_{conversation_id}.md"
    )

    OUTPUT_FILE.write_text(
        conversation["markdown"],
        encoding="utf-8",
    )

    print("\n--- Answer ---\n")
    print(conversation["markdown"])
    print(f"Saved → {OUTPUT_FILE}")

else:
    print("NO CONTENT RETURNED.")