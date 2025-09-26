# AI Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `ai` block integrates Large Language Models (LLMs) directly into your workflow. It can be used for a wide range of tasks, from simple text generation and classification to powering complex, multi-turn conversational agents that can use external tools.

**General Syntax:**

```hcl
ai "unique_ai_block_id" {
    model = "gpt-4o-mini"
    prompt = \`Your detailed instructions for the AI.\`
    variable = "variable_to_store_response"
    next = "success_handler_node"
    next_failed = "error_handler_node"   // Optional
    next_expired = "timeout_handler_node" // Optional
}
```

## 2. Properties

- **`model`** (Required): A QuotedString specifying the AI model to use (e.g., "gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo").
- **`prompt`** (Required): The instructions for the AI model, provided as a TemplateLiteral or Heredoc. This is the most critical part of the block and should be crafted carefully.
- **`variable`** (Required): The name of the variable where the AI's final response will be stored in memory.
- **`expiration`** (Optional): ISO 8601 duration string (e.g., "PT1H" for 1 hour) specifying when the task should timeout.
- **`supports_pdf`** (Optional): Boolean literal indicating whether the AI can process PDF files.
- **`mcps`** (Optional): An array of Model Context Protocol (MCP) connections that provide the AI with external tools and capabilities.
- **`functions`** (Optional): An array of specific functions the AI is allowed to call.
- **`next`** (Required): The node ID to transition to after the AI task completes successfully.
- **`next_failed`** (Optional): The node ID to transition to if the AI model returns an error.
- **`next_expired`** (Optional): The node ID to transition to if the task times out.

## 3. AI Agents vs. AI Tasks

The `ai` block can function in two distinct modes depending on the prompt's design:

- **AI Task**: A single, one-shot request to the LLM. It performs a specific action (e.g., summarize text, classify intent, extract data) and immediately returns a result. It does not engage in a conversation.
- **AI Agent**: A more advanced, conversational component designed for multi-turn interactions. An agent maintains context, follows a process, and can use tools. It only terminates its execution when a specific goal is met or the user wishes to exit.

## 4. Prompt Engineering Best Practices

The quality of your AI's output depends heavily on the quality of your prompt.

### 4.1. Structure of an Agent Prompt

For the best results with AI Agents, structure your prompt with these five components:

- **Context**: What is the overall goal? What problem is the agent solving?
- **Role**: What "personality" or tone should the agent adopt? (e.g., "You are a helpful and friendly bank teller.")
- **Process**: What specific steps must the agent follow to resolve the user's request?
- **Conditions**: What are the rules or constraints? When should it not do something?
- **Closure**: How does the agent know when its job is done? This is typically handled by calling a specific function like end_function.

### 4.2. Critical Instruction for Agents with Tools

If your agent uses `mcps` or `functions`, you must include an explicit instruction telling it not to end the conversation prematurely.

**Example Instruction:**

```
IMPORTANTE: Solo termina la conversación cuando el usuario explícitamente diga que quiere salir, terminar, o abandonar la conversación. En ese caso, ejecuta end_function con {"accion": "salir", "motivo": "usuario_solicito_salir"}.
```

## 5. MCP (Model Context Protocol) Support

The AI block supports MCP connections through the `mcps` property, which allows the AI model to access external tools and services. MCP connections extend the AI's capabilities beyond text generation to include actions like API calls, database queries, file operations, and more.

### 5.1. MCP Configuration Formats

The `mcps` property accepts an array of MCP connection definitions in three formats:

**1. Simple URL String:** For basic MCP connections without authentication

```hcl
mcps = [
    "https://mcp.jelou.ai/mcp"
]
```

**2. Object with URL:** For explicit URL specification

```hcl
mcps = [
    { url = "https://api.example.com/mcp" }
]
```

**3. Object with URL and Headers:** For authenticated MCP connections

```hcl
mcps = [
    {
        url = "https://secure.api/mcp"
        headers = {
            Authorization = "Bearer ${env.API_TOKEN}",
            "X-Customer-Id" = "customer-123",
            "Content-Type" = "application/json"
        }
    }
]
```

### 5.2. MCP Requirements

- **URL Format**: Must use HTTP or HTTPS protocol
- **Endpoint**: Must end with `/mcp` for streamable HTTP support
- **Validation**: URLs are validated during compilation
- **Headers**: Support environment variable interpolation (`${env.VARIABLE_NAME}`)

### 5.3. Example with Multiple MCP Connections

```hcl
ai "multi_tool_agent" {
    model = "gpt-4o"
    prompt = `You have access to multiple tools. Help the user with their request.
  
    IMPORTANTE: Solo termina la conversación cuando el usuario explícitamente diga que quiere salir, terminar, o abandonar la conversación. En ese caso, ejecuta end_function con {"accion": "salir", "motivo": "usuario_solicito_salir"}.`
    variable = "agent_response"
    mcps = [
        "https://mcp.jelou.ai/mcp",                    // Basic connection
        { url = "https://database.api/mcp" },          // Database tools
        {                                              // Authenticated API
            url = "https://secure.external.api/mcp"
            headers = {
                Authorization = "Bearer ${env.EXTERNAL_API_TOKEN}",
                "X-Client-Version" = "v2.1"
            }
        }
    ]
    next = "process_agent_response"
}
```

## 6. Functions Support

The AI block supports function calling through the `functions` property, which allows the AI model to access external functions and services.

### 6.1. Function Configuration Formats

The `functions` property accepts an array of function definitions in three formats:

**1. Simple Name String:** For basic functions without authentication

```hcl
functions = [
    "function-name"
]
```

**2. Object with Name:** For explicit function specification

```hcl
functions = [
    { name = "function-name" }
]
```

**3. Object with Name and Headers:** For authenticated functions

```hcl
functions = [
    {
        name = "function-name"
        headers = {
            Authorization = "Bearer ${env.API_TOKEN}",
            "X-Customer-Id" = "customer-123",
            "Content-Type" = "application/json"
        }
    }
]
```

### 6.2. Example with Multiple Functions

```hcl
ai "ai_function_agent" {
    model = "gpt-4o"
    prompt = `You have access to multiple functions. Help the user with their request.
  
    IMPORTANTE: Solo termina la conversación cuando el usuario explícitamente diga que quiere salir, terminar, o abandonar la conversación. En ese caso, ejecuta end_function con {"accion": "salir", "motivo": "usuario_solicito_salir"}.`
    variable = "agent_response"
    functions = [
        "send_interactive_message",
        { name = "database_query" },
        {
            name = "external_api_call"
            headers = {
                Authorization = "Bearer ${env.EXTERNAL_API_TOKEN}",
                "X-Client-Version" = "v2.1"
            }
        }
    ]
    next = "process_agent_response"
}
```

## 7. Available Execution Context

When writing prompts, you can reference various context variables and APIs that are available during execution:

### 7.1. Memory and Context Variables

- **`{{$memory.variable_name}}`**: Access variables stored in workflow memory
- **`{{$context.variable_name}}`**: Access execution context variables
- **`{{$message.text}}`**: Access the current user message text
- **`{{$user.property}}`**: Access user properties
- **`{{$bot.property}}`**: Access bot properties
- **`{{$company.property}}`**: Access company properties
- **`{{$env.VARIABLE_NAME}}`**: Access environment variables

### 7.2. Utility Functions (Available in Code Blocks)

When using external code files or inline code, these utilities are available:

- **`$utils.dayjs`**: Date manipulation library
- **`$utils._`**: Lodash utility library
- **`$utils.crypto`**: Cryptographic functions
- **`$utils.logger`**: Logging functionality
- **`$utils.shortly`**: URL shortening

## 8. Example Usage

### Example 1: AI Agent for Data Collection

This agent engages in a conversation to collect the user's name and email.

```hcl
ai "collect_user_data_agent" {
    model = "gpt-4o"
    prompt = \`
        You are a friendly registration assistant. Your goal is to collect the user's full name and email address.

        PROCESS:
        1. Greet the user and ask for their full name.
        2. After they provide their name, ask for their email address.
        3. Once you have both pieces of information, validate the email format looks correct. If not, ask again politely.
        4. When you have a valid name and email, you MUST end your execution.

        CLOSURE:
        When you have successfully collected the name and email, you must call the end_function with this exact JSON structure:
        {"name": "[user's full name]", "email": "[user's email]"}
    \`
    variable = "collected_data"
    next = "process_registration"
    next_failed = "handle_agent_error"
}

}

// Subsequent node can now use {{$memory.collected_data.name}} and {{$memory.collected_data.email}}
```

### Example 2: AI Task for Intent Routing

This task classifies a user's message into a predefined category without a conversation.

```hcl
ai "intent_router_task" {
    model = "gpt-4o-mini"
    prompt = \`
        You are an AI router. Your job is to classify the user's message into one of the following categories: "cards", "accounts", or "other".

        User message: "{{$memory.user_message_text}}"

        You must respond with only a JSON object with a single key "flow".

        Example:
        - User message: "I want to apply for a credit card" -> {"flow": "cards"}
        - User message: "How do I open a savings account?" -> {"flow": "accounts"}
        - User message: "What's the weather like?" -> {"flow": "other"}
    \`
    variable = "routing_decision"
    next = "conditional_router"
}

// A conditional block can now use {{$memory.routing_decision.flow}} to direct the workflow.
```

## 9. Advanced Agent Examples

### 9.1. FAQ (Frequently Asked Questions) Agent

For providing context-aware responses about a company or service:

```hcl
ai "faq_agent" {
    model = "gpt-4o"
    prompt = `You are an advisor for [client name], [client description], who must respond to user queries.

Always respond to queries in a [tone, personality] manner.

When the user asks you a query, you must always follow this process:
1. Search for context about [client name] in the files you have available.
2. Determine if the information you obtain is relevant to the user's query. Be very careful in this step, as you must clearly define whether this information is relevant or not.

IMPORTANTE: Solo termina la conversación cuando el usuario explícitamente diga que quiere salir, terminar, o abandonar la conversación. En ese caso, ejecuta end_function con {"accion": "salir", "motivo": "usuario_solicito_salir"}.

Consider the following guidelines for your interaction:
- If you don't find information about a service, assume that [business name] does not provide that service.
- You are part of [client name], therefore you can speak in first person.`
    variable = "faq_response"
    next = "process_faq_response"
}
```

### 9.2. User Routing Agent

For intelligent workflow routing based on user intent:

```hcl
ai "routing_agent" {
    model = "gpt-4o-mini"
    prompt = `You are an AI router that must process a client message to decide which specialized agent to send them to.

There are 5 agents:
1. Credit cards (issuance, general information about cards or American Express / AMEX)
2. Savings and checking accounts (openings and general information)
3. Documents (certificates, account statements)
4. General inquiries (general inquiries about the bank)
5. Other

Try as much as possible to place them in some agent, and only if the message is very generic, you can choose 5 (other).

If the message is not understood or is very ambiguous, ask the user again in kind words.

You must always end your execution by calling end_function with a JSON schema: { flow: [flow] }.

Flow can be equal to "cards", "accounts", "documents", "inquiries", and "other".

Examples:
- If user makes inquiries about credit cards, end with end_function { flow: "cards" }
- If user asks for a bank certificate, end with end_function { flow: "documents" }`
    variable = "routing_decision"
    next = "process_routing"
}
```

### 9.3. Data Collection Agent

For structured data gathering processes:

```hcl
ai "data_collection_agent" {
    model = "gpt-4o"
    prompt = `You must request the user's name and email address.

When the user provides their name and email, execute your end_function with the JSON schema:
{"name": [name], "email": [email]}

IMPORTANTE: Solo termina la conversación cuando el usuario explícitamente diga que quiere salir, terminar, o abandonar la conversación. En ese caso, ejecuta end_function con {"accion": "salir", "motivo": "usuario_solicito_salir"}.`
    variable = "user_data"
    next = "validate_user_data"
}
```

## 10. Model-Specific Considerations

### 10.1. GPT-4o-mini Considerations

GPT-4o-mini requires more specific and explicit prompts compared to larger models:

- **Simplify logic**: Avoid complex conditional structures
- **Avoid complex nested instructions**: Keep instructions linear and clear
- **Explicitly repeat key instructions**: Don't assume the model will remember context
- **Use concrete examples**: Provide specific examples rather than abstract concepts

**Example for GPT-4o-mini:**

```hcl
ai "mini_agent" {
    model = "gpt-4o-mini"
    prompt = `You are a customer service agent. Your job is simple:

1. Ask the user what they need help with
2. If they ask about balance, respond with balance information
3. If they ask about transfers, respond with transfer information
4. If they ask about anything else, say you cannot help with that

Always be polite and helpful.

When you are done helping, call end_function with {"status": "completed"}.`
    variable = "mini_response"
    next = "process_response"
}
```

### 10.2. GPT-4.1 Best Practices

GPT-4.1 follows instructions more literally and requires explicit guidance:

**Key Improvements for GPT-4.1:**

1. **Persistence Instructions**: Include explicit agent persistence

```
You are an agent. Only end your execution when you're sure you've completely resolved the user's request.
```

2. **Tool Usage Instructions**: Be explicit about tool usage

```
If you're not sure, use your available tools to get the information. Don't invent.
```

3. **Planning Instructions**: Encourage step-by-step thinking

```
You must plan explicitly before each function call, and reflect after each action. Don't chain actions without thinking.
```

**Example GPT-4.1 Optimized Prompt:**

```hcl
ai "gpt41_agent" {
    model = "gpt-4.1"
    prompt = `# Instructions

You are an agent. Only end your execution when you're sure you've completely resolved the user's request.

If you're not sure, use your available tools to get the information. Don't invent.

You must plan explicitly before each function call, and reflect after each action. Don't chain actions without thinking.

## Your Role
You are a helpful customer service representative.

## Process
1. Carefully analyze the user's query step by step
2. Identify what information you need
3. Use appropriate tools to gather information
4. Provide a complete response
5. Only end when the user is satisfied

## Output Format
Always structure your responses clearly with sections when appropriate.`
    variable = "gpt41_response"
    next = "process_response"
}
```

## 11. Smart Prompt Design Patterns

### 11.1. Avoiding Conditional Logic in Prompts

Instead of including complex conditional logic in your prompts, preprocess conditions using code blocks:

**❌ Avoid this pattern:**

```hcl
ai "bad_example" {
    model = "gpt-4o"
    prompt = `If you have data in {{$memory.variable}}, then do such thing, otherwise, follow these other instructions.

If {{$memory.user_type}} equals "premium", then provide premium support, otherwise provide standard support.`
    variable = "response"
    next = "next_node"
}
```

**✅ Better approach:**

```hcl
code "prepare_conditional_prompt" {
    runtime = "javascript"
    code = `
        let conditionalPrompt = "Provide standard support.";
    
        if ($memory.get("user_type") === "premium") {
            conditionalPrompt = "Provide premium support with advanced features.";
        }
    
        $memory.set("conditionalPrompt", conditionalPrompt);
    `
    next = "ai_agent_with_conditional"
}

ai "ai_agent_with_conditional" {
    model = "gpt-4o"
    prompt = `You are a customer service agent.

{{$memory.conditionalPrompt}}

Follow these instructions carefully and provide excellent service.`
    variable = "agent_response"
    next = "process_response"
}
```

### 11.2. Benefits of Smart Design

- **Reduces model cognitive load**: The AI focuses on its core task rather than decision logic
- **Decreases token usage**: Eliminates redundant conditional instructions
- **Increases prompt clarity**: Clean, focused prompts perform better
- **Improves response consistency**: Preprocessed logic is more reliable

### 11.3. Optimization Guidelines

1. **Be precise and concise**: Short, clear prompts outperform long, redundant ones
2. **Avoid determinism**: Don't expect identical responses; use AI for guidance, not fixed outputs
3. **Include clear termination instructions**: Explicitly state when and how the agent should end
4. **Optimize token usage**: Remove unnecessary repetitions and variables from prompts

## 12. Function Usage Best Practices

### 12.1. Native Tools

For built-in functions like `send_interactive_message`, provide necessary parameters:

```json
Use the send_interactive_message tool with these parameters:
{
  "caption": "<for lists, this is the button name>",
  "text": "<main text>",
  "title": "<text above the button/list>",
  "options": [
    {
      "title": "<option name, required>",
      "description": "<description, optional>"
    }
  ]
}
```

### 12.2. End Function Usage

Always use the complete function name `end_function` with clear output parameters:

```hcl
ai "completion_agent" {
    model = "gpt-4o"
    prompt = `Complete the user's request.

When finished, call end_function with a JSON object containing:
- status: "success" or "error"
- data: any relevant output data
- message: a summary of what was accomplished

Example: end_function({"status": "success", "data": {"user_id": "123"}, "message": "User registration completed"})`
    variable = "completion_result"
    next = "handle_completion"
}
```
