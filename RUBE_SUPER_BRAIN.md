# PROJECT RUBE: MASTER ARCHITECTURE KNOWLEDGE
INSTRUCTIONS: The following context is divided into XML tags. Always read the relevant <source> tags before generating system code or proposing logic.

<source url='https://langchain-ai.github.io/langgraph/'>
Skip to main content
Docs by LangChain home pageOpen source
Search...
Ctrl K
  *   *   * Try LangSmith
  * Try LangSmith


Search...
Navigation
LangGraph overview
Deep AgentsLangChainLangGraphIntegrationsLearnReferenceContribute
Python
  * Overview


##### Get started
  * Install
  * Quickstart
  * Local server
  * Changelog
  * Thinking in LangGraph
  * Workflows + agents


##### Capabilities
  * Persistence
  * Durable execution
  * Streaming
  * Interrupts
  * Time travel
  * Memory
  * Subgraphs


##### Production
  * Application structure
  * Test
  * LangSmith Studio
  * Agent Chat UI
  * LangSmith Deployment
  * LangSmith Observability


##### LangGraph APIs
  * Graph API
  * Functional API
  * Runtime


On this page
  * Install
  * Core benefits
  * LangGraph ecosystem
  * Acknowledgements


# LangGraph overview
Copy page
Gain control with LangGraph to design agents that reliably handle complex tasks
Copy page
Trusted by companies shaping the future of agents— including Klarna, Replit, Elastic, and more— LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents. LangGraph is very low-level, and focused entirely on agent **orchestration**. Before using LangGraph, we recommend you familiarize yourself with some of the components used to build agents, starting with models and tools. We will commonly use LangChain components throughout the documentation to integrate models and tools, but you don’t need to use LangChain to use LangGraph. If you are just getting started with agents or want a higher-level abstraction, we recommend you use LangChain’s agents that provide prebuilt architectures for common LLM and tool-calling loops. LangGraph is focused on the underlying capabilities important for agent orchestration: durable execution, streaming, human-in-the-loop, and more.
## 
​
pip
uv
Copy
```
pip install -U langgraph

```

Then, create a simple hello world example:
Copy
```
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})

```

Use LangSmith to trace requests, debug agent behavior, and evaluate outputs. Set `LANGSMITH_TRACING=true` and your API key to get started.
## 
​
Core benefits
LangGraph provides low-level supporting infrastructure for _any_ long-running, stateful workflow or agent. LangGraph does not abstract prompts or architecture, and provides the following central benefits:
  * Durable execution: Build agents that persist through failures and can run for extended periods, resuming from where they left off.
  * Human-in-the-loop: Incorporate human oversight by inspecting and modifying agent state at any point.
  * Comprehensive memory: Create stateful agents with both short-term working memory for ongoing reasoning and long-term memory across sessions.
  * Debugging with LangSmith: Gain deep visibility into complex agent behavior with visualization tools that trace execution paths, capture state transitions, and provide detailed runtime metrics.
  * Production-ready deployment: Deploy sophisticated agent systems confidently with scalable infrastructure designed to handle the unique challenges of stateful, long-running workflows.


## 
​
LangGraph ecosystem
While LangGraph can be used standalone, it also integrates seamlessly with any LangChain product, giving developers a full suite of tools for building agents. To improve your LLM application development, pair LangGraph with:
## LangSmith Observability
Trace requests, evaluate outputs, and monitor deployments in one place. Prototype locally with LangGraph, then move to production with integrated observability and evaluation to build more reliable agent systems.
Learn more
## LangSmith Deployment
Deploy and scale agents effortlessly with a purpose-built deployment platform for long running, stateful workflows. Discover, reuse, configure, and share agents across teams — and iterate quickly with visual prototyping in Studio.
Learn more
## LangChain
Provides integrations and composable components to streamline LLM application development. Contains agent abstractions built on top of LangGraph.
Learn more
## 
​
Acknowledgements
LangGraph is inspired by Pregel and Apache Beam. The public interface draws inspiration from NetworkX. LangGraph is built by LangChain Inc, the creators of LangChain, but can be used without LangChain.
* * *
Edit this page on GitHub or file an issue.
Connect these docs to Claude, VSCode, and more via MCP for real-time answers.
Was this page helpful?
YesNo
Install LangGraph
Next
Ctrl+I
Docs by LangChain home page
githubxlinkedinyoutube
Resources
ForumChangelogLangChain AcademyTrust Center
Company
HomeAboutCareersBlog
githubxlinkedinyoutube

</source>

<source url='https://docs.crewai.com/'>
Skip to main content
CrewAI home page
v1.10.1
English
Search...
Ctrl KAsk AI
  *   * crewAIInc/crewAI
  * crewAIInc/crewAI


Search...
Navigation
Welcome
CrewAI Documentation
  * Website
  * Forum
  * Blog
  * CrewGPT


##### Welcome
  * CrewAI Documentation


Welcome
# CrewAI Documentation
Copy page
Build collaborative AI agents, crews, and flows — production ready from day one.
Copy page
# 
​
Ship multi‑agent systems with confidence
Design agents, orchestrate crews, and automate flows with guardrails, memory, knowledge, and observability baked in.
Get startedView changelogAPI Reference
## 
​
Get started
## Introduction
Overview of CrewAI concepts, architecture, and what you can build with agents, crews, and flows.
## Installation
Install via `uv`, configure API keys, and set up the CLI for local development.
## Quickstart
Spin up your first crew in minutes. Learn the core runtime, project layout, and dev loop.
## 
​
Build the basics
## Agents
Compose agents with tools, memory, knowledge, and structured outputs using Pydantic. Includes templates and best practices.
## Flows
Orchestrate start/listen/router steps, manage state, persist execution, and resume long-running workflows.
## Tasks & Processes
Define sequential, hierarchical, or hybrid processes with guardrails, callbacks, and human-in-the-loop triggers.
## 
​
Enterprise journey
## Deploy automations
Manage environments, redeploy safely, and monitor live runs directly from the Enterprise console.
## Triggers & Flows
Connect Gmail, Slack, Salesforce, and more. Pass trigger payloads into crews and flows automatically.
## Team management
Invite teammates, configure RBAC, and control access to production automations.
## 
​
What’s new
## Triggers overview
Unified overview for Gmail, Drive, Outlook, Teams, OneDrive, HubSpot, and more — now with sample payloads and crews.
## Integration tools
Call existing CrewAI automations or Amazon Bedrock Agents directly from your crews using the updated integration toolkit.
Browse the examples and cookbooks for end-to-end reference implementations across agents, flows, and enterprise automations.
## 
​
Stay connected
## Star us on GitHub
If CrewAI helps you ship faster, give us a star and share your builds with the community.
## Join the community
Ask questions, showcase workflows, and request features alongside other builders.
Was this page helpful?
YesNo
Ctrl+I
websitexgithublinkedinyoutubereddit
Powered byThis documentation is built and hosted on Mintlify, a developer documentation platform
Assistant
Responses are generated using AI and may contain mistakes.

</source>

<source url='https://modelcontextprotocol.io/specification/'>
Skip to main content
Model Context Protocol home page
Search...
⌘K
  * Blog
  * GitHub


Search...
Navigation
About MCP
Versioning
DocumentationExtensionsSpecificationRegistrySEPsCommunity
##### Get started
  * What is MCP?


##### About MCP
  * Architecture
  * Servers
  * Clients
  * Versioning


##### Develop with MCP
  * Connect to local MCP servers
  * Connect to remote MCP Servers
  * Build an MCP server
  * Build an MCP client
  * SDKs
  * Security


##### Developer tools
  * MCP Inspector


On this page
  * Revisions
  * Negotiation


About MCP
# Versioning
Copy page
Copy page
The Model Context Protocol uses string-based version identifiers following the format `YYYY-MM-DD`, to indicate the last date backwards incompatible changes were made.
The protocol version will _not_ be incremented when the protocol is updated, as long as the changes maintain backwards compatibility. This allows for incremental improvements while preserving interoperability.
## 
​
Revisions
Revisions may be marked as:
  * **Draft** : in-progress specifications, not yet ready for consumption.
  * **Current** : the current protocol version, which is ready for use and may continue to receive backwards compatible changes.
  * **Final** : past, complete specifications that will not be changed.

The **current** protocol version is **2025-11-25**.
## 
​
Negotiation
Version negotiation happens during initialization. Clients and servers **MAY** support multiple protocol versions simultaneously, but they **MUST** agree on a single version to use for the session. The protocol provides appropriate error handling if version negotiation fails, allowing clients to gracefully terminate connections when they cannot find a version compatible with the server.
Was this page helpful?
YesNo
ClientsConnect to local MCP servers
⌘I
github

</source>

<source url='https://docs.anthropic.com/en/docs/build-with-claude/computer-use'>
  * Developer Guide
  * API Reference
  * MCP
  * Resources
  * Release Notes


EnglishLog in
Search...
⌘K
First steps
Intro to ClaudeQuickstart
Models & pricing
Models overviewChoosing a modelWhat's new in Claude 4.6Migration guideModel deprecationsPricing
Build with Claude
Features overviewUsing the Messages APIHandling stop reasonsPrompting best practices
Model capabilities
Extended thinkingAdaptive thinkingEffortFast mode (research preview)Structured outputsCitationsStreaming MessagesBatch processingPDF supportSearch resultsMultilingual supportEmbeddingsVision
Tools
OverviewHow to implement tool useWeb search toolWeb fetch toolCode execution toolMemory toolBash toolComputer use toolText editor tool
Tool infrastructure
Tool searchProgrammatic tool callingFine-grained tool streaming
Context management
Context windowsCompactionContext editingPrompt cachingToken counting
Files & assets
Files API
Agent Skills
OverviewQuickstartBest practicesSkills for enterpriseUsing Skills with the API
Agent SDK
OverviewQuickstartHow the agent loop works
Core concepts
Guides
SDK references
MCP in the API
MCP connectorRemote MCP servers
Claude on 3rd-party platforms
Amazon BedrockMicrosoft FoundryVertex AI
Prompt engineering
OverviewConsole prompting tools
Test & evaluate
Define success and build evaluationsUsing the Evaluation ToolReducing latency
Strengthen guardrails
Reduce hallucinationsIncrease output consistencyMitigate jailbreaksStreaming refusalsReduce prompt leak
Administration and monitoring
Admin API overviewData residencyWorkspacesUsage and Cost APIClaude Code Analytics APIZero Data Retention
Console
Log in
ToolsComputer use tool
Tools
# Computer use tool
Copy page
Copy page
Claude can interact with computer environments through the computer use tool, which provides screenshot capabilities and mouse/keyboard control for autonomous desktop interaction. On WebArena, a benchmark for autonomous web navigation across real websites, Claude achieves state-of-the-art results among single-agent systems, demonstrating strong ability to complete multi-step browser tasks end to end.
Computer use is in beta and requires a beta header:
  * `"computer-use-2025-11-24"` for Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5
  * `"computer-use-2025-01-24"` for Sonnet 4.5, Haiku 4.5, Opus 4.1, Sonnet 4, Opus 4, and Sonnet 3.7 (deprecated)


Reach out through the feedback form to share your feedback on this feature.
This feature is in beta and is **not** eligible for Zero Data Retention (ZDR). Beta features are excluded from ZDR.
## 
Overview
Computer use is a beta feature that enables Claude to interact with desktop environments. This tool provides:
  * **Screenshot capture** : See what's currently displayed on screen
  * **Mouse control** : Click, drag, and move the cursor
  * **Keyboard input** : Type text and use keyboard shortcuts
  * **Desktop automation** : Interact with any application or interface


While computer use can be augmented with other tools like bash and text editor for more comprehensive automation workflows, computer use specifically refers to the computer use tool's capability to see and control desktop environments.
## 
Model compatibility
Computer use is available for the following Claude models:
Model | Tool Version | Beta Flag  
---|---|---  
Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5 | `computer_20251124` | `computer-use-2025-11-24`  
All other supported models | `computer_20250124` | `computer-use-2025-01-24`  
Claude Opus 4.6, Claude Sonnet 4.6, and Claude Opus 4.5 introduce the `computer_20251124` tool version with new capabilities including the zoom action for detailed screen region inspection. All other models (Sonnet 4.5, Haiku 4.5, Sonnet 4, Opus 4, Opus 4.1, and Sonnet 3.7) use the `computer_20250124` tool version.
Older tool versions are not guaranteed to be backwards-compatible with newer models. Always use the tool version that corresponds to your model version.
## 
Security considerations
Computer use is a beta feature with unique risks distinct from standard API features. These risks are heightened when interacting with the internet.
To minimize risks, consider taking precautions such as:
  1. Using a dedicated virtual machine or container with minimal privileges to prevent direct system attacks or accidents.
  2. Avoiding giving the model access to sensitive data, such as account login information, to prevent information theft.
  3. Limiting internet access to an allowlist of domains to reduce exposure to malicious content.
  4. Asking a human to confirm decisions that may result in meaningful real-world consequences as well as any tasks requiring affirmative consent, such as accepting cookies, executing financial transactions, or agreeing to terms of service.


In some circumstances, Claude will follow commands found in content even if it conflicts with the user's instructions. For example, Claude instructions on webpages or contained in images may override instructions or cause Claude to make mistakes. Take precautions to isolate Claude from sensitive data and actions to avoid risks related to prompt injection.
The model has been trained to resist these prompt injections, and an extra layer of defense has been added. If you use the computer use tools, classifiers will automatically run on your prompts to flag potential instances of prompt injections. When these classifiers identify potential prompt injections in screenshots, they will automatically steer the model to ask for user confirmation before proceeding with the next action. This extra protection won't be ideal for every use case (for example, use cases without a human in the loop), so if you'd like to opt out and turn it off, please contact support.
These precautions remain important even with the classifier defense layer in place.
Inform end users of relevant risks and obtain their consent prior to enabling computer use in your own products.
Computer use reference implementation
Get started quickly with the computer use reference implementation that includes a web interface, Docker container, example tool implementations, and an agent loop.
**Note:** The implementation has been updated to include new tools for both Claude 4 models and Claude Sonnet 3.7. Be sure to pull the latest version of the repo to access these new features.
Use this form to provide feedback on the quality of the model responses, the API itself, or the quality of the documentation.
## 
Quick start
Here's how to get started with computer use:
Shell
```
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: computer-use-2025-11-24" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {
        "type": "computer_20251124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1
      },
      {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool"
      },
      {
        "type": "bash_20250124",
        "name": "bash"
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "Save a picture of a cat to my desktop."
      }
    ]
  }'
```

A beta header is only required for the computer use tool.
The example above shows all three tools being used together, which requires the beta header because it includes the computer use tool.
* * *
## 
How computer use works
  1. 1
Provide Claude with the computer use tool and a user prompt
     * Add the computer use tool (and optionally other tools) to your API request.
     * Include a user prompt that requires desktop interaction, for example, "Save a picture of a cat to my desktop."
  2. 2
Claude decides to use the computer use tool
     * Claude assesses if the computer use tool can help with the user's query.
     * If yes, Claude constructs a properly formatted tool use request.
     * The API response has a `stop_reason` of `tool_use`, signaling Claude's intent.
  3. 3
Extract tool input, evaluate the tool on a computer, and return results
     * On your end, extract the tool name and input from Claude's request.
     * Use the tool on a container or Virtual Machine.
     * Continue the conversation with a new `user` message containing a `tool_result` content block.
  4. 4
Claude continues calling computer use tools until it's completed the task
     * Claude analyzes the tool results to determine if more tool use is needed or the task has been completed.
     * If Claude decides it needs another tool, it responds with another `tool_use` `stop_reason` and you should return to step 3.
     * Otherwise, it crafts a text response to the user.


The repetition of steps 3 and 4 without user input is referred to as the "agent loop" (that is, Claude responding with a tool use request and your application responding to Claude with the results of evaluating that request).
### 
The computing environment
Computer use requires a sandboxed computing environment where Claude can safely interact with applications and the web. This environment includes:
  1. **Virtual display** : A virtual X11 display server (using Xvfb) that renders the desktop interface Claude will see through screenshots and control with mouse/keyboard actions.
  2. **Desktop environment** : A lightweight UI with window manager (Mutter) and panel (Tint2) running on Linux, which provides a consistent graphical interface for Claude to interact with.
  3. **Applications** : Pre-installed Linux applications like Firefox, LibreOffice, text editors, and file managers that Claude can use to complete tasks.
  4. **Tool implementations** : Integration code that translates Claude's abstract tool requests (like "move mouse" or "take screenshot") into actual operations in the virtual environment.
  5. **Agent loop** : A program that handles communication between Claude and the environment, sending Claude's actions to the environment and returning the results (screenshots, command outputs) back to Claude.


When you use computer use, Claude doesn't directly connect to this environment. Instead, your application:
  1. Receives Claude's tool use requests
  2. Translates them into actions in your computing environment
  3. Captures the results (screenshots, command outputs, etc.)
  4. Returns these results to Claude


For security and isolation, the reference implementation runs all of this inside a Docker container with appropriate port mappings for viewing and interacting with the environment.
* * *
## 
How to implement computer use
### 
Start with the reference implementation
A reference implementation is available that includes everything you need to get started quickly with computer use:
  * A containerized environment suitable for computer use with Claude
  * Implementations of the computer use tools
  * An agent loop that interacts with the Claude API and executes the computer use tools
  * A web interface to interact with the container, agent loop, and tools.


### 
Understanding the multi-agent loop
The core of computer use is the "agent loop" - a cycle where Claude requests tool actions, your application executes them, and returns results to Claude. Here's a simplified example:
```
async def sampling_loop(
    *,
    model: str,
    messages: list[dict],
    api_key: str,
    max_tokens: int = 4096,
    tool_version: str,
    thinking_budget: int | None = None,
    max_iterations: int = 10,  # Add iteration limit to prevent infinite loops
):
    """
    A simple agent loop for Claude computer use interactions.

    This function handles the back-and-forth between:
    1. Sending user messages to Claude
    2. Claude requesting to use tools
    3. Your app executing those tools
    4. Sending tool results back to Claude
    """
    # Set up tools and API parameters
    client = Anthropic(api_key=api_key)
    beta_flag = (
        "computer-use-2025-11-24"
        if "20251124" in tool_version
        else "computer-use-2025-01-24"
        if "20250124" in tool_version
        else "computer-use-2024-10-22"
    )

    # Configure tools - you should already have these initialized elsewhere
    tools = [
        {
            "type": f"computer_{tool_version}",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
        },
        {"type": f"text_editor_{tool_version}", "name": "str_replace_editor"},
        {"type": f"bash_{tool_version}", "name": "bash"},
    ]

    # Main agent loop (with iteration limit to prevent runaway API costs)
    iterations = 0
    while True and iterations < max_iterations:
        iterations += 1
        # Set up optional thinking parameter (for Claude Sonnet 3.7)
        thinking = None
        if thinking_budget:
            thinking = {"type": "enabled", "budget_tokens": thinking_budget}

        # Call the Claude API
        response = client.beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools,
            betas=[beta_flag],
            thinking=thinking,
        )

        # Add Claude's response to the conversation history
        response_content = response.content
        messages.append({"role": "assistant", "content": response_content})

        # Check if Claude used any tools
        tool_results = []
        for block in response_content:
            if block.type == "tool_use":
                # In a real app, you would execute the tool here
                # For example: result = run_tool(block.name, block.input)
                result = {"result": "Tool executed successfully"}

                # Format the result for Claude
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )

        # If no tools were used, Claude is done - return the final messages
        if not tool_results:
            return messages

        # Add tool results to messages for the next iteration with Claude
        messages.append({"role": "user", "content": tool_results})
```

The loop continues until either Claude responds without requesting any tools (task completion) or the maximum iteration limit is reached. This safeguard prevents potential infinite loops that could result in unexpected API costs.
Try the reference implementation out before reading the rest of this documentation.
### 
Optimize model performance with prompting
Here are some tips on how to get the best quality outputs:
  1. Specify simple, well-defined tasks and provide explicit instructions for each step.
  2. Claude sometimes assumes outcomes of its actions without explicitly checking their results. To prevent this you can prompt Claude with `After each step, take a screenshot and carefully evaluate if you have achieved the right outcome. Explicitly show your thinking: "I have evaluated step X..." If not correct, try again. Only when you confirm a step was executed correctly should you move on to the next one.`
  3. Some UI elements (like dropdowns and scrollbars) might be tricky for Claude to manipulate using mouse movements. If you experience this, try prompting the model to use keyboard shortcuts.
  4. For repeatable tasks or UI interactions, include example screenshots and tool calls of successful outcomes in your prompt.
  5. If you need the model to log in, provide it with the username and password in your prompt inside xml tags like `<robot_credentials>`. Using computer use within applications that require login increases the risk of bad outcomes as a result of prompt injection. Review the guide on mitigating prompt injections before providing the model with login credentials.


If you repeatedly encounter a clear set of issues or know in advance the tasks Claude will need to complete, use the system prompt to provide Claude with explicit tips or instructions on how to do the tasks successfully.
For agents that span multiple sessions, run end-to-end verification at the start of each session, not only after implementation. Browser-based checks catch regressions from prior sessions that code-level review alone misses. See Effective harnesses for long-running agents for details.
### 
System prompts
When one of the Anthropic-defined tools is requested via the Claude API, a computer use-specific system prompt is generated. It's similar to the tool use system prompt but starts with:
> You have access to a set of functions you can use to answer the user's question. This includes access to a sandboxed computing environment. You do NOT currently have the ability to inspect files or interact with external resources, except by invoking the below functions.
As with regular tool use, the user-provided `system_prompt` field is still respected and used in the construction of the combined system prompt.
### 
Available actions
The computer use tool supports these actions:
**Basic actions (all versions)**
  * **screenshot** - Capture the current display
  * **left_click** - Click at coordinates `[x, y]`
  * **type** - Type text string
  * **key** - Press key or key combination (for example, "ctrl+s")
  * **mouse_move** - Move cursor to coordinates


**Enhanced actions (`computer_20250124`)** Available in Claude 4 models and Claude Sonnet 3.7:
  * **scroll** - Scroll in any direction with amount control
  * **left_click_drag** - Click and drag between coordinates
  * **right_click** , **middle_click** - Additional mouse buttons
  * **double_click** , **triple_click** - Multiple clicks
  * **left_mouse_down** , **left_mouse_up** - Fine-grained click control
  * **hold_key** - Hold down a key for a specified duration (in seconds)
  * **wait** - Pause between actions


**Enhanced actions (`computer_20251124`)** Available in Claude Opus 4.6 and Claude Opus 4.5:
  * All actions from `computer_20250124`
  * **zoom** - View a specific region of the screen at full resolution. Requires `enable_zoom: true` in tool definition. Takes a `region` parameter with coordinates `[x1, y1, x2, y2]` defining top-left and bottom-right corners of the area to inspect.


### Example actions
### Modifier keys with click and scroll actions
### 
Tool parameters
Parameter | Required | Description  
---|---|---  
`type` | Yes | Tool version (`computer_20251124`, `computer_20250124`, or `computer_20241022`)  
`name` | Yes | Must be "computer"  
`display_width_px` | Yes | Display width in pixels  
`display_height_px` | Yes | Display height in pixels  
`display_number` | No | Display number for X11 environments  
`enable_zoom` | No | Enable zoom action (`computer_20251124` only). Set to `true` to allow Claude to zoom into specific screen regions. Default: `false`  
**Important:** The computer use tool must be explicitly executed by your application - Claude cannot execute it directly. You are responsible for implementing the screenshot capture, mouse movements, keyboard inputs, and other actions based on Claude's requests.
### 
Enable thinking capability in Claude 4 models and Claude Sonnet 3.7
Claude Sonnet 3.7 introduced a new "thinking" capability that allows you to see the model's reasoning process as it works through complex tasks. This feature helps you understand how Claude is approaching a problem and can be particularly valuable for debugging or educational purposes.
To enable thinking, add a `thinking` parameter to your API request:
```
"thinking": {
  "type": "enabled",
  "budget_tokens": 1024
}
```

The `budget_tokens` parameter specifies how many tokens Claude can use for thinking. This is subtracted from your overall `max_tokens` budget.
When thinking is enabled, Claude will return its reasoning process as part of the response, which can help you:
  1. Understand the model's decision-making process
  2. Identify potential issues or misconceptions
  3. Learn from Claude's approach to problem-solving
  4. Get more visibility into complex multi-step operations


Here's an example of what thinking output might look like:
```
[Thinking]
I need to save a picture of a cat to the desktop. Let me break this down into steps:

1. First, I'll take a screenshot to see what's on the desktop
2. Then I'll look for a web browser to search for cat images
3. After finding a suitable image, I'll need to save it to the desktop

Let me start by taking a screenshot to see what's available...
```

### 
Augmenting computer use with other tools
The computer use tool can be combined with other tools to create more powerful automation workflows. This is particularly useful when you need to:
  * Execute system commands (bash tool)
  * Edit configuration files or scripts (text editor tool)
  * Integrate with custom APIs or services (custom tools)


Shell
```
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: computer-use-2025-11-24" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 2000,
    "tools": [
      {
        "type": "computer_20251124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1
      },
      {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool"
      },
      {
        "type": "bash_20250124",
        "name": "bash"
      },
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "Find flights from San Francisco to a place with warmer weather."
      }
    ],
    "thinking": {
      "type": "enabled",
      "budget_tokens": 1024
    }
  }'
```

### 
Build a custom computer use environment
The reference implementation is meant to help you get started with computer use. It includes all of the components needed to have Claude use a computer. However, you can build your own environment for computer use to suit your needs. You'll need:
  * A virtualized or containerized environment suitable for computer use with Claude
  * An implementation of at least one of the Anthropic-defined computer use tools
  * An agent loop that interacts with the Claude API and executes the `tool_use` results using your tool implementations
  * An API or UI that allows user input to start the agent loop


#### 
Implement the computer use tool
The computer use tool is implemented as a schema-less tool. When using this tool, you don't need to provide an input schema as with other tools; the schema is built into Claude's model and can't be modified.
  1. 1
Set up your computing environment
Create a virtual display or connect to an existing display that Claude will interact with. This typically involves setting up Xvfb (X Virtual Framebuffer) or similar technology.
  2. 2
Implement action handlers
Create functions to handle each action type that Claude might request:
```
def handle_computer_action(action_type, params):
    if action_type == "screenshot":
        return capture_screenshot()
    elif action_type == "left_click":
        x, y = params["coordinate"]
        return click_at(x, y)
    elif action_type == "type":
        return type_text(params["text"])
    # ... handle other actions
```

  3. 3
Process Claude's tool calls
Extract and execute tool calls from Claude's responses:
```
for content in response.content:
    if content.type == "tool_use":
        action = content.input["action"]
        result = handle_computer_action(action, content.input)

        # Return result to Claude
        tool_result = {
            "type": "tool_result",
            "tool_use_id": content.id,
            "content": result,
        }
```

  4. 4
Implement the agent loop
Create a loop that continues until Claude completes the task:
```
while True:
    response = client.beta.messages.create(...)

    # Check if Claude used any tools
    tool_results = process_tool_calls(response)

    if not tool_results:
        # No more tool use, task complete
        break

    # Continue conversation with tool results
    messages.append({"role": "user", "content": tool_results})
```



#### 
Handle errors
When implementing the computer use tool, various errors may occur. Here's how to handle them:
### Screenshot capture failure
### Invalid coordinates
### Action execution failure
#### 
Handle coordinate scaling for higher resolutions
The API constrains images to a maximum of 1568 pixels on the longest edge and approximately 1.15 megapixels total (see image resizing for details). For example, a 1512x982 screen gets downsampled to approximately 1330x864. Claude analyzes this smaller image and returns coordinates in that space, but your tool executes clicks in the original screen space.
This can cause Claude's click coordinates to miss their targets unless you handle the coordinate transformation.
To fix this, resize screenshots yourself and scale Claude's coordinates back up:
Python
```
import math


def get_scale_factor(width, height):
    """Calculate scale factor to meet API constraints."""
    long_edge = max(width, height)
    total_pixels = width * height

    long_edge_scale = 1568 / long_edge
    total_pixels_scale = math.sqrt(1_150_000 / total_pixels)

    return min(1.0, long_edge_scale, total_pixels_scale)


# When capturing screenshot
scale = get_scale_factor(screen_width, screen_height)
scaled_width = int(screen_width * scale)
scaled_height = int(screen_height * scale)

# Resize image to scaled dimensions before sending to Claude
screenshot = capture_and_resize(scaled_width, scaled_height)


# When handling Claude's coordinates, scale them back up
def execute_click(x, y):
    screen_x = x / scale
    screen_y = y / scale
    perform_click(screen_x, screen_y)
```

#### 
Follow implementation best practices
### Use appropriate display resolution
### Implement proper screenshot handling
### Add action delays
### Validate actions before execution
### Log actions for debugging
* * *
## 
Understand computer use limitations
The computer use functionality is in beta. While Claude's capabilities are cutting edge, developers should be aware of its limitations:
  1. **Latency** : the current computer use latency for human-AI interactions may be too slow compared to regular human-directed computer actions. Focus on use cases where speed isn't critical (for example, background information gathering, automated software testing) in trusted environments.
  2. **Computer vision accuracy and reliability** : Claude may make mistakes or hallucinate when outputting specific coordinates while generating actions. Claude Sonnet 3.7 introduces the thinking capability that can help you understand the model's reasoning and identify potential issues.
  3. **Tool selection accuracy and reliability** : Claude may make mistakes or hallucinate when selecting tools while generating actions or take unexpected actions to solve problems. Additionally, reliability may be lower when interacting with niche applications or multiple applications at once. Prompt the model carefully when requesting complex tasks.
  4. **Scrolling reliability** : Claude Sonnet 3.7 introduced dedicated scroll actions with direction control that improves reliability. The model can now explicitly scroll in any direction (up/down/left/right) by a specified amount.
  5. **Spreadsheet interaction** : Mouse clicks for spreadsheet interaction have improved in Claude Sonnet 3.7 with the addition of more precise mouse control actions like `left_mouse_down`, `left_mouse_up`, and new modifier key support. Cell selection can be more reliable by using these fine-grained controls and combining modifier keys with clicks.
  6. **Account creation and content generation on social and communications platforms** : While Claude will visit websites, Claude's ability to create accounts or generate and share content or otherwise engage in human impersonation across social media websites and platforms is limited. This capability may be updated in the future.
  7. **Vulnerabilities** : Vulnerabilities like jailbreaking or prompt injection may persist across frontier AI systems, including the beta computer use API. In some circumstances, Claude will follow commands found in content, sometimes even in conflict with the user's instructions. For example, Claude instructions on webpages or contained in images may override instructions or cause Claude to make mistakes. Consider the following: a. Limiting computer use to trusted environments such as virtual machines or containers with minimal privileges b. Avoiding giving computer use access to sensitive accounts or data without strict oversight c. Informing end users of relevant risks and obtaining their consent before enabling or requesting permissions necessary for computer use features in your applications
  8. **Inappropriate or illegal actions** : Per Anthropic's terms of service, you must not employ computer use to violate any laws or the Acceptable Use Policy.


Always carefully review and verify Claude's computer use actions and logs. Do not use Claude for tasks requiring perfect precision or sensitive user information without human oversight.
* * *
## 
Pricing
Computer use follows the standard tool use pricing. When using the computer use tool:
**System prompt overhead** : The computer use beta adds 466-499 tokens to the system prompt
**Computer use tool token usage** :
Model | Input tokens per tool definition  
---|---  
Claude 4.x models | 735 tokens  
Claude Sonnet 3.7 (deprecated) | 735 tokens  
**Additional token consumption** :
  * Screenshot images (see Vision pricing)
  * Tool execution results returned to Claude


If you're also using bash or text editor tools alongside computer use, those tools have their own token costs as documented in their respective pages.
## 
Next steps
Reference implementation
Get started quickly with the complete Docker-based implementation
Tool documentation
Learn more about tool use and creating custom tools
Was this page helpful?
  * Overview
  * Model compatibility
  * Security considerations
  * Quick start
  * How computer use works
  * The computing environment
  * How to implement computer use
  * Start with the reference implementation
  * Understanding the multi-agent loop
  * Optimize model performance with prompting
  * System prompts
  * Available actions
  * Tool parameters
  * Enable thinking capability in Claude 4 models and Claude Sonnet 3.7
  * Augmenting computer use with other tools
  * Build a custom computer use environment
  * Understand computer use limitations
  * Pricing
  * Next steps


### Solutions
  * AI agents
  * Code modernization
  * Coding
  * Customer support
  * Education
  * Financial services
  * Government
  * Life sciences


### Partners
  * Amazon Bedrock
  * Google Cloud's Vertex AI


### Learn
  * Blog
  * Catalog
  * Courses
  * Use cases
  * Connectors
  * Customer stories
  * Engineering at Anthropic
  * Events
  * Powered by Claude
  * Service partners
  * Startups program


### Company
  * Anthropic
  * Careers
  * Economic Futures
  * Research
  * News
  * Responsible Scaling Policy
  * Security and compliance
  * Transparency


### Learn
  * Blog
  * Catalog
  * Courses
  * Use cases
  * Connectors
  * Customer stories
  * Engineering at Anthropic
  * Events
  * Powered by Claude
  * Service partners
  * Startups program


### Help and security
  * Availability
  * Status
  * Support
  * Discord


### Terms and policies
  * Privacy policy
  * Responsible disclosure policy
  * Terms of service: Commercial
  * Terms of service: Consumer
  * Usage policy



</source>

<source url='https://docs.llamaindex.ai/en/stable/'>
Skip to content
LlamaIndex OSS Documentation 
⌘K
All Sections Framework Agents LlamaParse
TwitterLinkedInBlueskyGitHub
Select theme Dark Light Auto
  * LlamaParse
    * Welcome to LlamaParse
    * Parse
      * Overview of Parse
      * Getting Started
      * LlamaParse API v2 Guide
      * Migration Guide: Parse Upload Endpoint v1 to v2
      * Supported Document Types
      * LlamaParse FAQ
      * Basics
        * Tiers
        * Retrieving Results
      * Input Options
        * Crop Box
        * Page Ranges
        * HTML Options
        * Spreadsheet Options
        * Presentation Options
        * Cache Control
      * Output Options
        * Markdown Output Options
        * Spatial Text Output Options
        * Tables as Spreadsheet Options
        * Embedded Images Options
        * Screenshots Options
        * Retrieving Exported PDF
        * Extract Printed Page Numbers
        * Webhook Configurations
      * Processing Options
        * Ignore Options
        * OCR Options
        * Table Extraction
        * Custom Prompt
        * Specialized Chart Parsing
        * Processing Control
      * Examples
        * LlamaParse Examples
        * Quick Start: Parse a PDF & Interpret Outputs
        * Parse All PDFs in a Folder with LlamaParse
        * Parse Charts in PDFs and Analyze with Pandas
        * Parse with Additional Prompts
      * v1
        * Features
          * Parsing options
          * Multimodal Parsing
          * Python Usage
          * Layout Extraction
          * Metadata
          * Cache options
          * Structured Output (Beta)
          * Webhook
          * Job predictability
          * Selecting what to parse
          * LlamaParse Document Pipeline Triggers
          * Parsing instructions (deprecated)
          * Prompts
        * Examples
          * LlamaParse Examples with llama-cloud-services
          * Parse All PDFs in a Folder with LlamaParse
          * Parse and Analyze Excel Spreadsheets with LlamaParse
          * Parse with Additional Prompts
    * Extract
      * Getting Started
        * Getting Started
        * Using the Web UI
        * SDK Usage
        * REST API
      * Features
        * LlamaExtract Core Concepts
        * Schema Design and Restrictions
        * Configuration Options
        * Metadata Extensions
        * Performance Tips
      * Examples
        * LlamaExtract Examples
        * Auto-Generate Schema for Extraction
        * Extract Data from Financial Reports - with Citations and Reasoning
        * Extracting Repeating Entities with Table Row Extaction
        * Resume Book Processing Agent
      * LlamaExtract Privacy
    * Classify
      * Getting Started
        * Getting Started
        * Classify SDK
      * Examples
        * LlamaClassify Examples
        * Classify Contract Types
    * Split
      * Getting Started
        * Getting Started
        * API/SDK Usage
      * Examples
        * Splitting Concatenated Documents
        * Split Examples
    * Index
      * Getting Started
      * Usage Guides
        * Index Usage Guides
        * Index Status Monitoring
        * Index API & Clients Guide
        * Index Framework Integration
        * Index No-code UI Guide
      * How-to Guides
        * Files
          * Extracting Figures from Documents
      * Examples
        * Index Examples
        * Building RAG Applications with Index & Agents
      * Integrations
        * Data Sinks
          * Data Sinks
          * AstraDB
          * Azure AI Search
          * Managed Data Sink
          * Milvus
          * MongoDB Atlas Vector Search
          * Pinecone
          * Postgres
          * Qdrant
        * Data Sources
          * Data Sources
          * Azure Blob Storage Data Source
          * Box Storage Data Source
          * Confluence Data Source
          * File Upload Data Source
          * Google Drive Data Source
          * Jira Data Source
          * Microsoft OneDrive Data Source
          * S3 Data Source
          * Microsoft SharePoint Data Source
        * Embedding Models
          * Embedding Models
          * Azure Embedding
          * Bedrock Embedding
          * Cohere Embedding
          * Gemini Embedding
          * HuggingFace Embedding
          * OpenAI Embedding
      * Multi-Environments
      * Parsing & Transformation
      * Retrieval
        * Basic
        * Retrieval Modes
        * Advanced
        * Composite Retrieval
        * Image Retrieval
    * Sheets
      * Examples
        * LlamaSheets Examples
        * Using LlamaSheets with Coding Agents
        * Using LlamaSheets with Custom Agents and Workflows
      * Getting Started
    * General
      * API Key
      * Pricing
      * Organizations
      * Regions
      * Billing and Usage
      * Webhooks
      * Rate Limits
    * Self-Hosting
      * Quick Start
      * Frequently Asked Questions
      * Architecture
      * Cloud-Specific Guides
        * Overview
        * Azure Deployment
          * Azure Setup Guide
          * Validation Guide
          * Troubleshooting Guide
      * Configuration
        * Auth
        * File Storage
        * Ingress
        * Databases and Queues
          * Overview
          * Azure Service Bus as Job Queue
        * LLM Integrations
          * Overview
          * OpenAI Setup
          * Azure OpenAI Setup
          * Anthropic API Setup
          * AWS Bedrock Setup
          * Google Gemini API Setup
          * Google Vertex AI Setup
          * Centralized Provider Configuration
        * Autoscaling
        * Global Admin Setup
      * Monitoring
        * Monitoring
      * Tuning
        * Service Configurations
        * LlamaParse Configuration
        * LlamaParse Configuration - Throughput
    * Cookbooks
      * Cookbooks
      * Enterprise Rollout
    * LlamaParse Reference 🔗
  * LlamaAgents New
    * Overview
    * Agent Workflows
      * Introduction
      * Branches and loops
      * Managing State
      * Streaming events
      * Concurrent execution of workflows
      * Human in the Loop
      * Customizing entry and exit points
      * Drawing a Workflow
      * Resource Objects
      * Retry steps execution
      * Workflows from unbound functions
      * Run Your Workflow as a Server
      * Python Client
      * Writing durable workflows
      * DBOS Durable Execution
      * Writing async workflows
      * Observability
    * Cloud
      * Agent Builder
      * Click-to-Deploy from LlamaCloud
      * Agent Data
      * Agent Data (Python)
      * Agent Data (JavaScript)
    * llamactl
      * Getting Started
      * Agent Templates
      * Serving your Workflows
      * Configuring a UI
      * Workflow React Hooks
      * Deployment Config Reference
      * Continuous Deployment with GitHub Actions
    * llamactl Reference
      * init
      * serve
      * deployments
      * auth
      * auth env
      * pkg
    * Agent Workflows Reference 🔗
  * LlamaIndex Framework
    * Welcome to LlamaIndex 🦙 !
    * Getting Started
      * High-Level Concepts
      * Installation and Setup
      * How to read these docs
      * Starter Tutorial (Using OpenAI)
      * Starter Tutorial (Using Local LLMs)
      * Discover LlamaIndex Video Series
      * Frequently Asked Questions (FAQ)
      * Starter Tools
        * Starter Tools
        * RAG CLI
      * Async Programming in Python
    * Learn
      * Building an LLM application
      * Using LLMs
      * Building agents
        * Building an agent
        * Using existing tools
        * Maintaining state
        * Streaming output and events
        * Human in the loop
        * Multi-agent patterns in LlamaIndex
        * Using Structured Output
      * Building a RAG pipeline
        * Introduction to RAG
        * Indexing
          * Indexing
        * Loading
          * Loading Data (Ingestion)
          * Loading from LlamaCloud
          * LlamaHub
        * Querying
          * Querying
        * Storing
          * Storing
      * Structured Data Extraction
        * Introduction to Structured Data Extraction
        * Using Structured LLMs
        * Structured Prediction
        * Low-level structured data extraction
        * Structured Input
      * Tracing And Debugging
        * Tracing and Debugging
      * Evaluating
        * Cost Analysis
          * Cost Analysis
          * Usage Pattern
        * Evaluating
      * Putting It All Together
        * Putting It All Together
        * Agents
        * Apps
          * Full-Stack Web Application
          * A Guide to Building a Full-Stack Web App with LLamaIndex
          * A Guide to Building a Full-Stack LlamaIndex Web App with Delphic
        * Chatbots
          * How to Build a Chatbot
        * Q And A
          * Q&A patterns
          * A Guide to Extracting Terms and Definitions
        * Structured Data
          * Structured Data
      * Privacy and Security
    * Use Cases
      * Use Cases
      * Agents
      * Chatbots
      * Structured Data Extraction
      * Fine-tuning
      * Querying Graphs
      * Multi-modal
      * Prompting
      * Question-Answering (RAG)
      * Querying CSVs
      * Parsing Tables and Charts
      * Text to SQL
    * Component Guides
      * Component Guides
      * Deploying
        * Agents
          * Agents
          * Memory
          * Module Guides
          * Tools
        * Chat Engines
          * Chat Engine
          * Module Guides
          * Usage Pattern
        * Query Engine
          * Query Engine
          * Module Guides
          * Response Modes
          * Streaming
          * Supporting Modules
          * Usage Pattern
      * Evaluating
        * Evaluating
        * Contributing A `LabelledRagDataset`
        * Evaluating Evaluators with `LabelledEvaluatorDataset`'s
        * Evaluating With `LabelledRagDataset`'s
        * Modules
        * Usage Pattern (Response Evaluation)
        * Usage Pattern (Retrieval)
      * Indexing
        * Indexing
        * Document Management
        * How Each Index Works
        * LlamaCloudIndex + LlamaCloudRetriever
        * Using a Property Graph Index
        * Metadata Extraction
        * Module Guides
        * Using VectorStoreIndex
      * Loading
        * Loading Data
        * Connector
          * Data Connectors (LlamaHub)
          * LlamaParse
          * Module Guides
          * Usage Pattern
        * Documents And Nodes
          * Documents / Nodes
          * Defining and Customizing Documents
          * Metadata Extraction Usage Pattern
          * Defining and Customizing Nodes
        * Ingestion Pipeline
          * Ingestion Pipeline
          * Transformations
        * Node Parsers
          * Node Parser Usage Pattern
          * Node Parser Modules
        * SimpleDirectoryReader
      * MCP
        * Model Context Protocol (MCP)
        * Converting Existing LlamaIndex Workflows & Tools to MCP
        * LlamaCloud MCP Servers & Tools
        * Using MCP Tools with LlamaIndex
      * Models
        * Models
        * Embeddings
        * Llms
          * Using LLMs
          * Using local models
          * Available LLM integrations
          * Customizing LLMs within LlamaIndex Abstractions
          * Using LLMs as standalone modules
        * Multi-modal models
        * Prompts
          * Prompts
          * Prompt Usage Pattern
      * Observability
        * Observability
        * Callbacks
          * Callbacks
          * Token Counting - Migration Guide
        * Instrumentation
      * Querying
        * Querying
        * Node Postprocessors
          * Node Postprocessor
          * Node Postprocessor Modules
        * Response Synthesizers
          * Response Synthesizer
          * Response Synthesis Modules
        * Retriever
          * Retriever
          * Retriever Modes
          * Retriever Modules
        * Router
          * Routers
        * Structured Outputs
          * Structured Outputs
          * Output Parsing Modules
          * Pydantic Programs
          * (Deprecated) Query Engines + Pydantic Outputs
      * Storing
        * Storing
        * Chat Stores
        * Customizing Storage
        * Document Stores
        * Index Stores
        * Key-Value Stores
        * Persisting & Loading Data
        * Vector Stores
      * Supporting Modules
        * Migrating from ServiceContext to Settings
        * Configuring Settings
        * Supporting Modules
    * Open Source Community
      * FAQ
        * Frequently Asked Questions
        * Chat Engines
        * Documents and Nodes
        * Embeddings
        * Large Language Models
        * Query Engines
        * Vector Database
      * Full-Stack Projects
      * Integrations
        * Integrations
        * ChatGPT Plugin Integrations
        * Unit Testing LLMs/RAG With DeepEval
        * Fleet Context Embeddings - Building a Hybrid Search Engine for the Llamaindex Library
        * Using Graph Stores
        * Tracing with Graphsignal
        * Guidance
        * LM Format Enforcer
        * Using Managed Indices
        * Tonic Validate
        * Evaluating and Tracking with TruLens
        * Perform Evaluations on LlamaIndex with UpTrain
        * Using Vector Stores
      * Llama Packs
        * Llama Packs 🦙📦
    * Integrations
      * Embeddings
        * Aleph Alpha Embeddings 
        * Anyscale Embeddings 
        * Baseten Embeddings 
        * Bedrock Embeddings 
        * Embeddings with Clarifai 
        * Cloudflare Workers AI Embeddings 
        * CohereAI Embeddings 
        * Custom Embeddings 
        * DashScope Embeddings 
        * Databricks Embeddings 
        * DeepInfra 
        * Elasticsearch Embeddings 
        * Qdrant FastEmbed Embeddings 
        * Fireworks Embeddings 
        * Google Gemini Embeddings 
        * GigaChat 
        * Google GenAI Embeddings 
        * Google Palm Embeddings 
        * Heroku LLM Managed Inference Embedding 
        * Local Embeddings with HuggingFace 
        * IBM watsonx.ai 
        * Local Embeddings with IPEX-LLM on Intel CPU 
        * Local Embeddings with IPEX-LLM on Intel GPU 
        * Isaacus Embeddings 
        * Jina 8K Context Window Embeddings 
        * Jina Embeddings 
        * LangChain Embeddings 
        * Llamafile Embeddings 
        * LLMRails Embeddings 
        * MistralAI Embeddings 
        * Mixedbread AI Embeddings 
        * ModelScope Embeddings 
        * Nebius Embeddings 
        * Netmind AI Embeddings 
        * Nomic Embedding 
        * NVIDIA NIMs 
        * Oracle Cloud Infrastructure (OCI) Data Science Service 
        * Oracle Cloud Infrastructure Generative AI 
        * Ollama Embeddings 
        * OpenAI Embeddings 
        * Local Embeddings with OpenVINO 
        * Optimized Embedding Model using Optimum-Intel 
        * Oracle AI Vector Search: Generate Embeddings 
        * PremAI Embeddings 
        * Interacting with Embeddings deployed in Amazon SageMaker Endpoint with LlamaIndex 
        * Text Embedding Inference 
        * TextEmbed - Embedding Inference Server 
        * Together AI Embeddings 
        * Upstage Embeddings 
        * Interacting with Embeddings deployed in Vertex AI Endpoint with LlamaIndex 
        * VoyageAI Embeddings 
        * YandexGPT 
      * Llm
        * AI21 
        * Aleph Alpha 
        * Anthropic 
        * Anthropic Prompt Caching 
        * Anyscale 
        * Apertis 
        * ASI LLM 
        * Azure AI model inference 
        * Azure OpenAI 
        * Baseten Cookbook 
        * Bedrock 
        * Bedrock Converse 
        * Cerebras 
        * Clarifai LLM 
        * Cleanlab Trustworthy Language Model 
        * Cohere 
        * CometAPI 
        * DashScope LLMS 
        * Databricks 
        * DeepInfra 
        * DeepSeek 
        * EverlyAI 
        * Featherless AI LLM 
        * Fireworks 
        * Fireworks Function Calling Cookbook 
        * Friendli 
        * Gemini 
        * Google GenAI 
        * Grok 4 
        * Groq 
        * Helicone AI Gateway 
        * Heroku LLM Managed Inference 
        * Hugging Face LLMs 
        * IBM watsonx.ai 
        * IPEX-LLM on Intel CPU 
        * IPEX-LLM on Intel GPU 
        * Konko 
        * LangChain LLM 
        * LiteLLM 
        * Replicate - Llama 2 13B 
        * 🦙 x 🦙 Rap Battle 
        * Llama API 
        * LlamaCPP 
        * llamafile 
        * LLM Predictor 
        * LM Studio 
        * LocalAI 
        * Maritalk 
        * MistralRS LLM 
        * MistralAI 
        * ModelScope LLMS 
        * Monster API <> LLamaIndex 
        * MyMagic AI LLM 
        * Nebius LLMs 
        * Netmind AI LLM 
        * Neutrino AI 
        * NVIDIA NIMs 
        * NVIDIA NIMs 
        * NVIDIA TensorRT-LLM 
        * NVIDIA LLM Text Completion API 
        * NVIDIA Triton 
        * Oracle Cloud Infrastructure Data Science 
        * Oracle Cloud Infrastructure Generative AI 
        * OctoAI 
        * Ollama LLM 
        * Ollama - Gemma 
        * OpenAI 
        * OpenAI JSON Mode vs. Function Calling for Data Extraction 
        * OpenAI Responses API 
        * OpenRouter 
        * OpenVINO LLMs 
        * OpenVINO GenAI LLMs 
        * Optimum Intel LLMs optimized with IPEX backend 
        * Using Opus 4.1 with LlamaIndex 
        * AlibabaCloud-PaiEas 
        * PaLM 
        * Perplexity 
        * [Pipeshift](https://pipeshift.com) 
        * Portkey 
        * Predibase 
        * PremAI LlamaIndex 
        * Client of Baidu Intelligent Cloud's Qianfan LLM Platform 
        * RunGPT 
        * Interacting with LLM deployed in Amazon SageMaker Endpoint with LlamaIndex 
        * SambaNova Systems 
        * Together AI LLM 
        * Upstage 
        * Vercel AI Gateway 
        * Vertex AI 
        * Replicate - Vicuna 13B 
        * vLLM 
        * Xorbits Inference 
        * Yi LLMs 
      * Retrievers
        * Auto Merging Retriever 
        * Comparing Methods for Structured Retrieval (Auto-Retrieval vs. Recursive Retrieval) 
        * Bedrock (Knowledge Bases) 
        * BM25 Retriever 
        * Composable Objects 
        * Activeloop Deep Memory 
        * Ensemble Retrieval Guide 
        * Chunk + Document Hybrid Retrieval with Long-Context Embeddings (Together.ai) 
        * Pathway Retriever 
        * Reciprocal Rerank Fusion Retriever 
        * Recursive Retriever + Node References + Braintrust 
        * Recursive Retriever + Node References 
        * Relative Score Fusion and Distribution-Based Score Fusion 
        * Router Retriever 
        * Simple Fusion Retriever 
        * Auto-Retrieval from a Vectara Index 
        * Vertex AI Search Retriever 
        * connect to VideoDB 
        * You.com Retriever 
      * Vector stores
        * Alibaba Cloud MySQL 
        * Alibaba Cloud OpenSearch Vector Store 
        * Google AlloyDB for PostgreSQL - `AlloyDBVectorStore` 
        * Amazon Neptune - Neptune Analytics vector store 
        * AnalyticDB 
        * ApertureDB as a Vector Store with LlamaIndex. 
        * Astra DB 
        * Simple Vector Store - Async Index Creation 
        * Awadb Vector Store 
        * Test delete 
        * Azure AI Search 
        * Azure CosmosDB MongoDB Vector Store 
        * Azure Cosmos DB No SQL Vector Store 
        * Azure Postgres Vector Store 
        * Bagel Vector Store 
        * Bagel Network 
        * Baidu VectorDB 
        * Cassandra Vector Store 
        * Auto-Retrieval from a Vector Database 
        * Chroma Vector Store 
        * Chroma + Fireworks + Nomic with Matryoshka embedding 
        * Chroma 
        * ClickHouse Vector Store 
        * Google Cloud SQL for PostgreSQL - `PostgresVectorStore` 
        * Couchbase Vector Store 
        * DashVector Vector Store 
        * Databricks Vector Search 
        * IBM Db2 Vector Store and Vector Search 
        * Deep Lake Vector Store Quickstart 
        * DocArray Hnsw Vector Store 
        * DocArray InMemory Vector Store 
        * Dragonfly and Vector Store 
        * DuckDB 
        * Auto-Retrieval from a Vector Database 
        * Elasticsearch 
        * Elasticsearch Vector Store 
        * Epsilla Vector Store 
        * Existing data
          * Guide: Using Vector Store Index with Existing Pinecone Vector Store 
          * Guide: Using Vector Store Index with Existing Weaviate Vector Store 
        * Faiss Vector Store 
        * Firestore Vector Store 
        * Gel Vector Store 
        * Hnswlib 
        * Hologres 
        * Jaguar Vector Store 
        * Advanced RAG with temporal filters using LlamaIndex and KDB.AI vector store 
        * LanceDB Vector Store 
        * Lantern Vector Store (auto-retriever) 
        * Lantern Vector Store 
        * Lindorm 
        * Milvus Vector Store with Async API 
        * Milvus Vector Store with Full-Text Search 
        * Milvus Vector Store With Hybrid Search 
        * Milvus Vector Store 
        * Milvus Vector Store - Metadata Filter 
        * MongoDB Atlas Vector Store 
        * MongoDB Atlas + Fireworks AI RAG Example 
        * MongoDB Atlas + OpenAI RAG Example 
        * Moorcheh Vector Store Demo 
        * MyScale Vector Store 
        * Neo4j Vector Store - Metadata Filter 
        * Neo4j vector store 
        * Nile Vector Store (Multi-tenant PostgreSQL) 
        * ObjectBox VectorStore Demo 
        * OceanBase Vector Store 
        * Opensearch Vector Store 
        * Oracle AI Vector Search: Vector Store 
        * pgvecto.rs 
        * A Simple to Advanced Guide with Auto-Retrieval (with Pinecone + Arize Phoenix) 
        * Pinecone Vector Store - Metadata Filter 
        * Pinecone Vector Store 
        * Pinecone Vector Store - Hybrid Search 
        * Postgres Vector Store 
        * Hybrid Search with Qdrant BM42 
        * Qdrant Hybrid Search 
        * Hybrid RAG with Qdrant: multi-tenancy, custom sharding, distributed setup 
        * Qdrant Vector Store - Metadata Filter 
        * Qdrant Vector Store - Default Qdrant Filters 
        * Qdrant Vector Store 
        * Redis Vector Store 
        * Relyt 
        * Rockset Vector Store 
        * S3VectorStore Integration 
        * Simple Vector Store 
        * Local Llama2 + VectorStoreIndex 
        * Llama2 + VectorStoreIndex 
        * Simple Vector Stores - Maximum Marginal Relevance Retrieval 
        * S3/R2 Storage 
        * Supabase Vector Store 
        * TablestoreVectorStore 
        * Tair Vector Store 
        * Tencent Cloud VectorDB 
        * TiDB Vector Store 
        * Timescale Vector Store (PostgreSQL) 
        * txtai Vector Store 
        * Typesense Vector Store 
        * Upstash Vector Store 
        * load documents 
        * 1. Installation 
        * Google Vertex AI Vector Search 
        * Google Vertex AI Vector Search v2.0 
        * Vespa Vector Store demo 
        * Auto-Retrieval from a Weaviate Vector Database 
        * Weaviate Vector Store Metadata Filter 
        * Weaviate Vector Store 
        * Weaviate Vector Store - Hybrid Search 
        * **WordLift** Vector Store 
        * Zep Vector Store 
    * ChangeLog
    * Framework Reference 🔗
  * MCP Docs Search


TwitterLinkedInBlueskyGitHub
Select theme Dark Light Auto
On this page Overview 
  * Overview
  * Introduction
    * What are agents?
    * What are workflows?
    * What is context augmentation?
    * LlamaIndex is the framework for Context-Augmented LLM Applications
  * Use cases
    * 👨‍👩‍👧‍👦 Who is LlamaIndex for?
  * Getting Started
    * 30 second quickstart
  * LlamaCloud
  * Community
    * Getting the library
    * Contributing
  * LlamaIndex Ecosystem


## On this page
  * Overview
  * Introduction
    * What are agents?
    * What are workflows?
    * What is context augmentation?
    * LlamaIndex is the framework for Context-Augmented LLM Applications
  * Use cases
    * 👨‍👩‍👧‍👦 Who is LlamaIndex for?
  * Getting Started
    * 30 second quickstart
  * LlamaCloud
  * Community
    * Getting the library
    * Contributing
  * LlamaIndex Ecosystem


# Welcome to LlamaIndex 🦙 !
Copy as Markdown
MCP Server
Copy MCP URL  Install in Cursor  Copy Claude config  Copy Codex config 
LlamaIndex is the leading framework for building LLM-powered agents over your data with LLMs and workflows.
  * Introduction
What is context augmentation? What are agents and workflows? How does LlamaIndex help build them?
  * Use cases
What kind of apps can you build with LlamaIndex? Who should use it?
  * Getting started
Get started in Python or TypeScript in just 5 lines of code!
  * LlamaCloud
Managed services for LlamaIndex including LlamaParse, the world’s best document parser.
  * Community
Get help and meet collaborators on Discord, Twitter, LinkedIn, and learn how to contribute to the project.
  * Related projects
Check out our library of connectors, readers, and other integrations at LlamaHub as well as demos and starter apps like create-llama.


## Introduction
Section titled “Introduction”
### What are agents?
Section titled “What are agents?”
Agents are LLM-powered knowledge assistants that use tools to perform tasks like research, data extraction, and more. Agents range from simple question-answering to being able to sense, decide and take actions in order to complete tasks.
LlamaIndex provides a framework for building agents including the ability to use RAG pipelines as one of many tools to complete a task.
### What are workflows?
Section titled “What are workflows?”
Workflows are multi-step processes that combine one or more agents, data connectors, and other tools to complete a task. They are event-driven software that allows you to combine RAG data sources and multiple agents to create a complex application that can perform a wide variety of tasks with reflection, error-correction, and other hallmarks of advanced LLM applications. You can then deploy these agentic workflows as production microservices.
### What is context augmentation?
Section titled “What is context augmentation?”
LLMs offer a natural language interface between humans and data. LLMs come pre-trained on huge amounts of publicly available data, but they are not trained on **your** data. Your data may be private or specific to the problem you’re trying to solve. It’s behind APIs, in SQL databases, or trapped in PDFs and slide decks.
Context augmentation makes your data available to the LLM to solve the problem at hand. LlamaIndex provides the tools to build any of context-augmentation use case, from prototype to production. Our tools allow you to ingest, parse, index and process your data and quickly implement complex query workflows combining data access with LLM prompting.
The most popular example of context-augmentation is Retrieval-Augmented Generation or RAG, which combines context with LLMs at inference time.
### LlamaIndex is the framework for Context-Augmented LLM Applications
Section titled “LlamaIndex is the framework for Context-Augmented LLM Applications”
LlamaIndex imposes no restriction on how you use LLMs. You can use LLMs as auto-complete, chatbots, agents, and more. It just makes using them easier. We provide tools like:
  * **Data connectors** ingest your existing data from their native source and format. These could be APIs, PDFs, SQL, and (much) more.
  * **Data indexes** structure your data in intermediate representations that are easy and performant for LLMs to consume.
  * **Engines** provide natural language access to your data. For example: 
    * Query engines are powerful interfaces for question-answering (e.g. a RAG flow).
    * Chat engines are conversational interfaces for multi-message, “back and forth” interactions with your data.
  * **Agents** are LLM-powered knowledge workers augmented by tools, from simple helper functions to API integrations and more.
  * **Observability/Evaluation** integrations that enable you to rigorously experiment, evaluate, and monitor your app in a virtuous cycle.
  * **Workflows** allow you to combine all of the above into an event-driven system far more flexible than other, graph-based approaches.


## Use cases
Section titled “Use cases”
Some popular use cases for LlamaIndex and context augmentation in general include:
  * Question-Answering (Retrieval-Augmented Generation aka RAG)
  * Chatbots
  * Document Understanding and Data Extraction
  * Autonomous Agents that can perform research and take actions
  * Multi-modal applications that combine text, images, and other data types
  * Fine-tuning models on data to improve performance


Check out our use cases documentation for more examples and links to tutorials.
### 👨‍👩‍👧‍👦 Who is LlamaIndex for?
Section titled “👨‍👩‍👧‍👦 Who is LlamaIndex for?”
LlamaIndex provides tools for beginners, advanced users, and everyone in between.
Our high-level API allows beginner users to use LlamaIndex to ingest and query their data in 5 lines of code.
For more complex applications, our lower-level APIs allow advanced users to customize and extend any module — data connectors, indices, retrievers, query engines, and reranking modules — to fit their needs.
## Getting Started
Section titled “Getting Started”
LlamaIndex is available in Python (these docs) and Typescript. If you’re not sure where to start, we recommend reading how to read these docs which will point you to the right place based on your experience level.
### 30 second quickstart
Section titled “30 second quickstart”
Set an environment variable called `OPENAI_API_KEY` with an OpenAI API key. Install the Python library:
Terminal window```


pip install llama-index


```

Put some documents in a folder called `data`, then ask questions about them with our famous 5-line starter:
```


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader








documents = SimpleDirectoryReader("data").load_data()




index = VectorStoreIndex.from_documents(documents)




query_engine = index.as_query_engine()




response = query_engine.query("Some question about the data should go here")




print(response)


```

If any part of this trips you up, don’t worry! Check out our more comprehensive starter tutorials using remote APIs like OpenAI or any model that runs on your laptop.
## LlamaCloud
Section titled “LlamaCloud”
If you’re an enterprise developer, check out **LlamaCloud**. It is an end-to-end managed service for document parsing, extraction, indexing, and retrieval - allowing you to get production-quality data for your AI agent. You can sign up and get 10,000 free credits per month, sign up for one of our plans, or come talk to us if you’re interested in an enterprise solution. We offer both SaaS and self-hosted plans.
You can also check out the LlamaCloud documentation for more details.
  * **Document Parsing (LlamaParse)** : LlamaParse is the best-in-class document parsing solution. It’s powered by VLMs and perfect for even the most complex documents (nested tables, embedded charts/images, and more). Learn more or check out the docs.
  * **Document Extraction (LlamaExtract)** : Given a human-defined or inferred schema, extract structured data from any document. Learn more or check out the docs.
  * **Indexing/Retrieval** : Set up an e2e pipeline to index a collection of documents for retrieval. Connect your data source (e.g. Sharepoint, Google Drive, S3), your vector DB data sink, and we automatically handle the document processing and syncing. Learn more or check out the docs.


## Community
Section titled “Community”
Need help? Have a feature suggestion? Join the LlamaIndex community:
  * Twitter
  * Discord
  * LinkedIn


### Getting the library
Section titled “Getting the library”
  * LlamaIndex Python 
    * LlamaIndex Python Github
    * Python Docs (what you’re reading now)
    * LlamaIndex on PyPi
  * LlamaIndex.TS (Typescript/Javascript package): 
    * LlamaIndex.TS Github
    * TypeScript Docs
    * LlamaIndex.TS on npm


### Contributing
Section titled “Contributing”
We are open-source and always welcome contributions to the project! Check out our contributing guide for full details on how to extend the core library or add an integration to a third party like an LLM, a vector store, an agent tool and more.
## LlamaIndex Ecosystem
Section titled “LlamaIndex Ecosystem”
There’s more to the LlamaIndex universe! Check out some of our other projects:
  * llama_deploy | Deploy your agentic workflows as production microservices
  * LlamaHub | A large (and growing!) collection of custom data connectors
  * SEC Insights | A LlamaIndex-powered application for financial research
  * create-llama | A CLI tool to quickly scaffold LlamaIndex projects


Previous   
pkg Next   
High-Level Concepts

</source>

