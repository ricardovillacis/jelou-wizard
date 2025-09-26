# Input Block Documentation

**Last Updated:** 2025-08-04

## 1\. Overview

The `input` block is used to pause the workflow and wait for the user to provide a text-based response. The collected information is then stored in a memory variable for later use in the workflow, such as in a `conditional` block or an `http` request.

**General Syntax:**

```
input "unique_input_id" {
    prompt = "Your question for the user."
    variable = "variable_name_to_store_input"
    next = "next_node_id"
    next_expired = "timeout_handler_node" // Optional
    next_exit = "exit_handler_node"       // Optional
}
```

-----

## 2\. Properties

  * **`prompt`** (Required): The message displayed to the user, asking them for the information you need. This can be a `QuotedString`, `TemplateLiteral`, or `Heredoc`.
  * **`variable`** (Required): The name of the variable where the user's response will be stored in the workflow's memory. You can access this later using `{{$memory.variable_name_to_store_input}}`.
  * **`next`** (Required): The node ID to transition to after the user successfully provides input.
  * **`next_expired`** (Optional): The node ID to transition to if the user does not respond within the configured time limit. This is crucial for handling inactive users.
  * **`next_exit`** (Optional): The node ID to transition to if the user explicitly cancels the input action (if the channel supports such a feature).

-----

## 3\. Example Usage

This example asks for the user's email address, stores it, and then proceeds to a validation step.

```
// 1. Ask the user for their email
input "ask_for_email" {
    prompt = "Please enter your email address to continue:"
    variable = "user_email"
    next = "validate_email_format"
    next_expired = "handle_timeout"
}

// 2. A code block could then validate the stored email
code "validate_email_format" {
    runtime = "javascript"
    code = \`
        const email = $memory.get('user_email');
        const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        return { isValid: isValid };
    \`
    next = "check_validation_result"
}

// 3. A conditional block routes based on the validation
conditional "check_validation_result" {
    conditions = [
        {
            id = "is_valid_rule"
            terms = [{ operator = "equal", value1 = "{{isValid}}", value2 = true }]
            next = "thank_you_message"
        }
    ]
    next = "ask_for_email_again" // Default path if validation fails
}

message "handle_timeout" {
    type = text
    text = "It looks like you're busy. We can continue this later!"
    next = END
}
```