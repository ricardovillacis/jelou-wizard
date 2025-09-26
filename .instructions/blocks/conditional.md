# Conditional Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `conditional` block is a powerful routing tool that directs the workflow along different paths based on a set of logical rules. It evaluates conditions in order and executes the next path of the first rule that evaluates to true. If no rules match, it follows a default next path.

**General Syntax:**

```hcl
conditional "unique_conditional_id" {
    conditions = [
        {
            id = "rule_1"
            name = "rule_1"
            terms = [{ operator = "equal" value1 = "{{variable}}" value2 = "some_value" }]
            next = "path_for_rule_1"
        },
        {
            id = "rule_2"
            name = "rule_2"
            terms = [{ operator = "larger" value1 = "{{count}}" value2 = 10 }]
            next = "path_for_rule_2"
        }
    ]
    next = "default_path_if_no_match"
}
```

## 2. Properties

- **`conditions`** (Required): A list of one or more rule objects to be evaluated sequentially.
- **`next`** (Optional): The default node ID to transition to if none of the rules in the conditions list are met. If omitted and no rules match, the workflow may halt.

## 3. Rule Object Structure

Each object within the conditions list represents a single rule.Rule object properties are NOT separated by comma.

- **`id`** (Required): A unique identifier for the rule.
- **`name`** (Required): A human-readable description of the rule's purpose.
- **`terms`** (Required): A list containing one or more term objects that define the logic for the rule (term object is not separated by comma). For the rule to be true, all terms within this list must evaluate to true (an implicit AND).
- **`next`** (Required): The node ID to transition to if this rule is true.

Example

```
{
            id = "rule_1"
            name = "rule_1"
            terms = [{ operator = "equal" value1 = "{{variable}}" value2 = "some_value" }]
            next = "path_for_rule_1"
        }
```

### Term Object

Terms object properties are NOT separated by comma.

- **`operator`** (Required): The comparison operator to use.
- **`value1`** (Required): The first value for the comparison, typically a memory variable (e.g., "{{$memory.user_status}}").
- **`value2`** (Required): The second value for the comparison, which can be a static string, integer, boolean, or another memory variable.

Example:

```

{
                operator = "equal"
                value1 = "{{$memory.routing_decision.flow}}"
                value2 = "cards"
}
```

## 4. Supported Operators

| Operator          | Description                                                 | Example                                   |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------- |
| `equal`         | Checks if value1 is equal to value2.                        | value1 = "premium", value2 = "premium"    |
| `not_equal`     | Checks if value1 is not equal to value2.                    | value1 = "active", value2 = "inactive"    |
| `larger`        | Checks if value1 is greater than value2. (Numeric)          | value1 = 11, value2 = 10                  |
| `larger_equal`  | Checks if value1 is greater than or equal to value2.        | value1 = 10, value2 = 10                  |
| `smaller`       | Checks if value1 is less than value2. (Numeric)             | value1 = 9, value2 = 10                   |
| `smaller_equal` | Checks if value1 is less than or equal to value2.           | value1 = 10, value2 = 10                  |
| `contains`      | Checks if value1 (string) contains value2 (string).         | value1 = "hello world", value2 = "world"  |
| `not_contains`  | Checks if value1 does not contain value2.                   | value1 = "hello world", value2 = "galaxy" |
| `starts_with`   | Checks if value1 starts with value2.                        | value1 = "apple_pie", value2 = "apple"    |
| `ends_with`     | Checks if value1 ends with value2.                          | value1 = "apple_pie", value2 = "pie"      |
| `is_empty`      | Checks if value1 is empty or null. (value2 is ignored).     | value1 = ""                               |
| `is_not_empty`  | Checks if value1 is not empty or null. (value2 is ignored). | value1 = "has content"                    |

## 5. Example Usage

This example checks the result of an AI routing task and directs the user to the appropriate workflow.

```hcl
// An AI block runs first and saves its output to the 'routing_decision' variable.
// Let's assume it returned: { "flow": "cards" }

conditional "route_based_on_intent" {
    conditions = [
        {
            id = "rule_is_cards"
            name = "Check for credit card intent"
            terms = [{ 
                operator = "equal" 
                value1 = "{{$memory.routing_decision.flow}}" 
                value2 = "cards" 
            }]
            next = "go_to_cards_workflow"
        },
        {
            id = "rule_is_accounts"
            name = "Check for accounts intent"
            terms = [{ 
                operator = "equal" 
                value1 = "{{$memory.routing_decision.flow}}"
                value2 = "accounts" 
            }]
            next = "go_to_accounts_workflow"
        }
    ]
    // If the AI returned 'other' or something unexpected, this default path is taken.
    next = "handle_unclear_intent"
}

workflow "go_to_cards_workflow" {
    path = "cards/main.wf"
}

workflow "go_to_accounts_workflow" {
    path = "accounts/main.wf"
}

message "handle_unclear_intent" {
    type = text
    text = "I'm not sure how to help with that. Could you please rephrase your request?"
    next = "main_menu"
}
```
