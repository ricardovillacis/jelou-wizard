# Pause Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `pause` block temporarily halts the workflow's execution for a specified duration. This is useful for creating a more natural, human-like conversation flow, such as simulating typing delays or waiting for an external process to complete before proceeding.

**General Syntax:**

```hcl
pause "unique_pause_id" {
    duration = 5
    unit = "seconds"
    next = "next_node_id"
}
```

## 2. Properties

- **`duration`** (Required): An integer representing the length of the pause.
- **`unit`** (Required): A QuotedString specifying the unit of time for the duration. Valid options are:
  - `"seconds"`
  - `"minutes"`
  - `"hours"`
  - `"days"`
- **`next`** (Required): The node ID to transition to after the pause duration has elapsed.

## 3. Example Usage

This example demonstrates how to use a pause block to create a short delay between two messages, making the interaction feel less robotic.

```hcl
// 1. Send the initial message
message "initial_contact_message" {
    type = text
    text = "Let me look up your account details..."
    next = "wait_before_reply"
}

// 2. Pause for 3 seconds to simulate a search
pause "wait_before_reply" {
    duration = 3
    unit = "seconds"
    next = "send_account_details"
}

// 3. Send the follow-up message after the pause
message "send_account_details" {
    type = text
    text = "Thanks for waiting! I've found your account. Your balance is $1,234.56."
    next = END
}
```
