# Jelou Workflow DSL Reference

**Last Updated:** 2025-08-04

## 1. Introduction

This document is the high-level index for the Jelou Workflow DSL. It provides a summary of all available block types.

## 2. Core Concepts

### 2.1. Workflow Structure

All workflows use the following top-level structure, as defined in the grammar:

- `workflow "Name" { ... }`: Root block
- Required properties inside the block:
  - `channel = whatsapp | facebook | x | web | instagram`
  - `start = "NodeID"`
- Optional properties:
  - `inputs = [ { name, type, required?, description? }, ... ]`
- Body: zero or more node blocks (`message`, `input`, `location_request`, `marker`, `pause`, `http`, `code`, `ai`, `conditional`, `random`, `variable`, `datum`, `connect`, `ai_logic`, `workflow` (redirect), `tool`, `hsm`, `package`, `output`).

Example:

```
workflow "Task Manager Web" {
  channel = web
  start = "ask_task"

  input "ask_task" {
    prompt = "Ask the user for a task:"
    variable = "task"
    next = "save_task"
  }

  variable "save_task" {
    variables = {
      tasklist = "{{$memory.get('task')}}"
    }
    next = "ai_enc"
  }

  ai "ai_enc" {
    model = "gpt-4o-mini"
    prompt = `Give encouragement for task: {{$memory.get("task")}}`
    variable = "enc"
    next = "show"
  }

  message "show" {
    type = text
    text = "Encouragement: {{$memory.get('enc')}}" 
    next = END
  }
}
```

### 2.2. Routing (routes.yml)

The `routes.yml` file maps user intents to specific workflow files using a `defaults` section for fallbacks and a `routes` list for intent-based mapping. The `description` field in each route is critical for AI-powered intent recognition.

## 3. Block Reference Index

### 3.1. message

**Purpose:** Sends a message to the user, with various types like text, buttons, lists, and media.

**Docs:** For complete syntax, properties, and examples, see: `.instructions/blocks/message.md`

### 3.2. input

**Purpose:** Prompts the user for text input and stores it in a variable.

**Docs:** For complete syntax and properties, see: `.instructions/blocks/input.md`

### 3.3. location_request

**Purpose:** Prompts the user to share their geographical location.

**Docs:** For complete syntax and properties, see: `.instructions/blocks/location_request.md`

### 3.4. pause

**Purpose:** Pauses the workflow execution for a specified duration.

**Docs:** For complete syntax and properties, see: `.instructions/blocks/pause.md`

### 3.5. http

**Purpose:** Makes an HTTP request to an external service.

**Docs:** For complete syntax, properties, and examples, see: `.instructions/blocks/http.md`

### 3.6. code

**Purpose:** Executes a snippet of custom JavaScript code with access to workflow context.

**Docs:** For complete syntax, available APIs (`$memory`, `$utils`, etc.), and examples, see: `.instructions/blocks/code.md`

### 3.7. ai

**Purpose:** Interacts with an AI model for tasks like generation, classification, or acting as a conversational agent.

**Docs:** For complete syntax, prompt engineering best practices, and `end_function` usage, see: `.instructions/blocks/ai.md`

### 3.8. conditional

**Purpose:** Routes the workflow based on a set of logical conditions.

**Docs:** For complete syntax and operator examples, see: `.instructions/blocks/conditional.md`

### 3.9. random

**Purpose:** Randomly chooses one path from a list of weighted routes, ideal for A/B testing.

**Docs:** For complete syntax and properties, see: `.instructions/blocks/random.md`

### 3.10. variable

**Purpose:** Defines or modifies workflow variables in memory.

**Docs:** For complete syntax and examples, see: `.instructions/blocks/variable.md`

### 3.11. workflow

**Purpose:** Redirects execution to another `.wf` file, terminating the current one.

**Docs:** For complete syntax and usage patterns, see: `.instructions/blocks/workflow.md`

### 3.12. connect

**Purpose:** Connects the user to a live agent with configurable assignment strategies.

**Docs:** For complete syntax and error handling, see: `.instructions/blocks/connect.md`

### 3.13. package

**Purpose:** Executes a pre-built Marketplace Skill.

**Docs:** For complete syntax and input/output handling, see: `.instructions/blocks/package.md`
