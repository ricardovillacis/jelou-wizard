# Variable Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `variable` block is used to define, modify, or manipulate variables in the workflow's memory. This block provides a declarative way to set values, perform calculations, or transform data without writing custom JavaScript code. It's particularly useful for simple data operations and maintaining workflow state.

- **Keyword**: `variable`
- **NodeType**: `MEMORY`

The variable block supports two syntax styles:

### Style 1: Multi-variable Assignment (RecursiveObject)
```hcl
variable "set_initial_vars" {
    variables = {                           // (Required; RecursiveObject)
        user_score = 0,
        "session_id" = "initial_session",
        preferences = {
            theme = "dark",
            notifications_enabled = true
        }
    }
    next = "next_step_node"                 // (Optional)
}
```

Only the object-based syntax is supported by the grammar. The single-variable operation syntax is not supported (deprecated below for historical context).

### Syntax: Multi-variable Assignment (RecursiveObject)

### DEPRECATED: Single Variable Operations (Not Supported by Grammar)
The Peggy grammar only supports the object-based form using `variables = { ... }`. The single-variable syntax with `name`, `value`, `operation`, and related fields is not supported by the parser and should not be used.

## 2. Properties

### For Style 1 (Multi-variable Assignment):
- **`variables`** (Required): A RecursiveObject containing key-value pairs to set in memory. Supports nested objects and complex data structures.
- **`next`** (Optional): The node ID to transition to after the variable operation completes.

### Aliases and Flexible Keys (Normalized by Parser)
- **variables aliases**: `data`, `state`, `memory`, `context`, `values`, `config`, `settings`, `parameters`, `vars`, `storage`, `workflow_data`, `global_vars` → all normalized to `variables`.
- **next aliases**: `nextNode`, `next_node`, `continue_to`, `then`, `after` → all normalized to `next`.
- If `variables` is missing, the parser throws an error indicating the required property and suggests aliases.

## 3. (Removed) Single-variable Operations
Not supported by the grammar. Use the object-based `variables = { ... }` form instead.

## 4. Example Usage

### 4.1. Multi-variable Assignment (Style 1)

```hcl
// Set multiple variables at once
variable "initialize_session" {
    variables = {
        session_id = "sess_12345",
        user_status = "active",
        login_timestamp = "{{$utils.dayjs().toISOString()}}",
        settings = {
            theme = "dark",
            language = "en",
            notifications = {
                email = true,
                sms = false
            }
        }
    }
    next = "welcome_user"
}

// Set variables with mixed types
variable "set_user_data" {
    variables = {
        user_name = "John Doe",
        account_balance = 1500.50,
        is_premium = true,
        favorite_products = ["product1", "product2", "product3"],
        metadata = {
            source = "web",
            referrer = "google"
        }
    }
    next = "process_user_data"
}
```

### 4.2. (Removed) Single-variable Examples
Deprecated and not supported by the grammar.

### 4.3. (Removed) Numeric Operations Examples
Deprecated and not supported by the grammar.

### 4.4. (Removed) String Manipulation Examples
Deprecated and not supported by the grammar.

### 4.5. (Removed) Array Operations Examples
Deprecated and not supported by the grammar.

### 4.6. (Removed) Complex Data Structure Examples
Deprecated and not supported by the grammar.

## 5. Conditional Usage
Use the resulting variables from the object-based assignment with other blocks (e.g., conditional, code, message). Single-variable operations are not supported.

## 6. Data Validation
Validation is performed by the compiler/validators. There is no per-variable `type` or `operation` in the variable block.

## 7. Working with Memory Context
Access variables later via `{{$memory.variable_name}}` in other blocks.

## 8. RecursiveObject Structure

When using Style 1 with the `variables` property, you're working with a RecursiveObject. This structure allows for nested key-value pairs:

```hcl
variable "complex_data_structure" {
    variables = {
        key1 = "stringValue",
        "another key" = 123,                // Keys can be QuotedStrings or Identifiers
        is_enabled = true,
        nested_config = {
            inner_key = "inner_value",
            count = 42,
            deep_nested = {
                level = 3,
                data = ["item1", "item2"]
            }
        }
    }
    next = "process_complex_data"
}
```

**RecursiveObject Rules:**
- **Keys**: Can be `Identifier` or `QuotedString`
- **Values**: Can be `QuotedString`, `Int`, `BooleanLiteral`, arrays, or another `RecursiveObject`
- **Commas**: Use commas to separate key-value pairs (trailing comma is optional)
- **Nesting**: Objects can be nested to any depth

## 9. Best Practices

- **Use the Supported Syntax**: Only the object-based `variables = { ... }` form is supported.
- **Meaningful Names**: Use descriptive variable names that clearly indicate their purpose
- **Type Safety**: Specify the `type` property for important variables to catch errors early
- **Data Validation**: Validate user inputs before storing them in variables
- **Memory Management**: Clear or delete unnecessary variables to keep memory clean
- **Template Literals**: Use template literals for dynamic value construction
- **Error Handling**: Include `next_failed` paths for operations that might fail
- **Documentation**: Comment complex variable operations for future maintenance
- **Testing**: Test variable operations with different data types and edge cases

## 10. Common Patterns

### 10.1. Counter Pattern

```hcl
// Initialize counter
variable "init_counter" {
    name = "retry_count"
    value = 0
    operation = "set"
    next = "attempt_operation"
}

// Increment on retry
variable "increment_retry" {
    name = "retry_count"
    value = 1
    operation = "add"
    next = "check_retry_limit"
}
```

### 10.2. State Machine Pattern

```hcl
// Track workflow state
variable "set_state" {
    name = "workflow_state"
    value = "collecting_information"
    operation = "set"
    next = "continue_collection"
}

variable "advance_state" {
    name = "workflow_state"
    value = "validating_information"
    operation = "set"
    next = "validate_data"
}
```

### 10.3. Data Accumulation Pattern

```hcl
// Build up a list of selections
variable "add_selection" {
    name = "user_selections"
    value = "{{$memory.current_choice}}"
    operation = "append"
    next = "ask_for_more_choices"
}
```

### 10.4. Session Initialization Pattern (Style 1)

```hcl
// Initialize all session variables at once
variable "init_session" {
    variables = {
        session_id = "{{$utils.crypto.randomBytes(16).toString('hex')}}",
        start_time = "{{$utils.dayjs().toISOString()}}",
        user_ip = "{{$context.get('user_ip')}}",
        device_info = {
            platform = "{{$context.get('platform')}}",
            user_agent = "{{$context.get('user_agent')}}"
        },
        interaction_count = 0,
        last_activity = "{{$utils.dayjs().toISOString()}}"
    }
    next = "welcome_message"
}
```

## 11. Important Notes

- **Memory Access**: Access variables using `{{$memory.variable_name}}` in other blocks
- **Syntax**: Only the `variables = { ... }` object form is valid; single-variable operations are not supported
- **Variable Scope**: All variables are stored in the workflow's memory context and are accessible throughout the workflow execution