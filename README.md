# AlphaSense Research Monitor
```
I used AI as an assistant for documentation and code structure.
```
## Overview

This project is a lightweight research monitoring tool built with Python
and the AlphaSense Agent API.

It allows a user to enter a research question, submits the question to
GenSearch, polls the conversation until the research is complete, and
saves the returned Markdown response locally.

The monitor also stores the conversation ID and original research
question so future runs can continue the same conversation and ask what
has changed since the previous run.

## Why I Built It

I chose a monitoring workflow because it represents a practical support
and research use case.

Instead of manually repeating the same research query, the tool
maintains the context needed to revisit the topic and retrieve updated
information.

I intentionally kept the implementation lightweight and focused on the
core API workflow:

-   Authentication
-   GenSearch submission
-   Conversation polling
-   State persistence
-   Markdown output

## Project Structure

``` text
Alphasense_Monitor/
├── monitor.py
├── reports/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The `reports/` directory stores generated Markdown reports as well as
`monitor.json`, which contains the state needed to continue the
monitored research topic.

## Requirements

-   Python 3
-   `requests`
-   AlphaSense Agent API credentials

Install the required dependencies with:

``` bash
pip install -r requirements.txt
```

## Environment Variables

``` text
ALPHASENSE_API_KEY
ALPHASENSE_CLIENT_ID
ALPHASENSE_CLIENT_SECRET
ALPHASENSE_EMAIL
ALPHASENSE_PASSWORD
```

Credentials should be stored securely and should not be committed to
source control. The `.env.example` file can document the required
variable names without exposing credential values.

## Running the Monitor

Activate the virtual environment:

``` bash
source venv/bin/activate
```

Run the application:

``` bash
python monitor.py
```

On the first run, the program asks what the user would like to monitor.
The question is submitted to GenSearch, and the program receives a
conversation ID and polls the conversation until the research is
complete.

The completed Markdown response is saved inside the `reports/`
directory.

On a later run, the program checks for an existing `monitor.json` file.
If one exists, it retrieves the original research question and
conversation ID and submits a follow-up question asking what has changed
since the previous run.

## Design Decisions and Tradeoffs

- JSON instead of a .txt file for monitor state. You originally planned to save only conversation_id in a text file, then you realized: essentially, “wait, how will it know what we researched?” That led you to store both conversation_id and research_question in JSON. Tradeoff: slightly more state handling, but the monitor can actually reconstruct what it's monitoring.

- Reuse conversationId instead of starting a completely fresh research thread. I wanted the second run to ask “What has changed since the last run?” against the existing conversation. Why: it preserves the research context between runs.

- Polling instead of streaming. Polling worked better for a simple prototype. Tradeoff: straightforward implementation, but a production version should have timeout/retry/backoff handling.

- One predictable monitor.json instead of monitor_{conversation_id}.json. We realized there was a chicken-and-egg problem: on startup, you wouldn't know the conversation ID yet, so you wouldn't know which filename to look for. Tradeoff: simple lookup, but currently supports only one active monitor.

- Saving the GenSearch response as Markdown files. You wanted each completed research result stored locally rather than only printed to the terminal. That gives you persistent research output/history.

- Scheduling was deliberately left out of the MVP. The original monitor idea mentioned running on a schedule, but we decided the important prototype was first-run research → saved state → later follow-up. Tradeoff: not fully automated yet, but much smaller scope and easier to validate.

### Persisting Monitor State With JSON

I originally considered storing only the conversation ID in a text file.

While working through the monitor design, I realized that the
application also needed to remember the original research question.
Without it, the next run would know which conversation to continue but
would not know what topic was being monitored.

I changed the state file to JSON so both values could be stored
together:

``` json
{
  "conversation_id": "example-id",
  "research_question": "Example research question"
}
```

This keeps the implementation simple while still allowing the monitor to
maintain context between program executions.

A current tradeoff is that the project uses one `monitor.json` file,
meaning the prototype is designed around one active monitor. With more
development time, I would add support for multiple named monitors.

### Polling

I used polling because it provides a straightforward way to check the
status of an asynchronous GenSearch request.

The script checks conversation progress and waits two seconds between
requests until the operation reports completion.

For a production implementation, I would add stronger timeout, retry,
backoff, and rate-limit handling.

## Testing and Debugging

Because live API execution depends on valid AlphaSense credentials, I
separated some local functionality from the API workflow during
development.

I created a small test using a fake conversation ID and a dictionary
structured similarly to the expected response. This allowed me to verify
that the application could:

-   Create the reports directory
-   Build a file path using `pathlib`
-   Retrieve Markdown from the response structure
-   Write the Markdown to a `.md` file

I also used Python's compiler check:

``` bash
python -m py_compile monitor.py
```

to verify the completed script for Python syntax errors.

This helped isolate local application logic from API-dependent behavior
while building and debugging the prototype.

## What I Would Improve With More Time

With another week, I would focus on making the monitor more
production-ready:

-   Multiple named research monitors
-   Automatic scheduling
-   Timestamps and run history
-   Timeout handling
-   Retry and exponential backoff logic
-   Rate-limit handling
-   More detailed API error handling
-   Automated tests
-   More structured logging

I would also improve how monitor state and report history are managed so
users could easily compare research results across multiple runs.

## Current Status

The Python application structure, monitor state logic, polling workflow,
Markdown file handling, and syntax validation have been implemented.

Local file-writing behavior has also been tested independently using
simulated response data.

Live end-to-end execution requires valid AlphaSense Agent API
credentials.

# Feeback For Documentation