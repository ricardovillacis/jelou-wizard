# Connect Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `connect` block connects users to available operators/agents for live chat support with configurable assignment strategies and error handling. This is typically used when the automated workflow cannot handle the user's request or when they specifically request human assistance.

**General Syntax:**

```
connect "unique_connect_id" {
    team_id = 123                                    // (Required; NumberLiteral - ID of the team)
    priority = 5                                     // (Required; Integer - Priority level for the assignment)
    assignment_type = "direct"                       // (Required; QuotedString - "direct", "round_robin", etc.)
    assignment_by = "team"                          // (Required; QuotedString - "team", "shuffle", etc.)
    operator_not_found = "no_operator_message"      // (Optional; QuotedString - Node ID to go to when no operator is available)
    operator_not_in_scheduler = "out_of_hours"      // (Optional; QuotedString - Node ID to go to when operators are out of schedule)
    next_failed = "connection_failed_node"          // (Optional; QuotedString or END - General failure handler)
    next = "connection_successful_node"             // (Optional; QuotedString or END - Success handler)
}
```

## 2. Properties

### Required Properties

- **`team_id`**: The ID of the team to assign the conversation to (Required; NumberLiteral)
- **`priority`**: Priority level for the assignment, higher numbers typically mean higher priority (Required; Integer)
- **`assignment_type`**: The type of assignment strategy to use (Required; QuotedString)
  - Common values: `"direct"`, `"round_robin"`, `"load_balance"`
- **`assignment_by`**: How to assign the conversation (Required; QuotedString)
  - Common values: `"team"`, `"shuffle"`, `"skill"`, `"availability"`

### Optional Properties

- **`operator_not_found`**: Node to redirect to when no operators are available (Optional; QuotedString)
  - **Important**: This should reference a node that provides a helpful message to the user, not `END`
- **`operator_not_in_scheduler`**: Node to redirect to when operators are outside working hours (Optional; QuotedString)
  - **Important**: This should reference a node that explains the schedule or offers alternatives, not `END`
- **`next_failed`**: General failure handler for unknown connection errors (Optional; QuotedString or END)
- **`next`**: Success handler when connection is established (Optional; QuotedString or END)

## 3. Assignment Strategies

The connect block supports different assignment strategies through the `assignment_type` property:

- **`"direct"`**: Direct assignment to available operators
- **`"round_robin"`**: Distributes connections evenly among available agents
- **`"load_balance"`**: Assigns based on current workload distribution

The `assignment_by` property determines the assignment method:

- **`"team"`**: Assign based on team membership
- **`"shuffle"`**: Random assignment within available operators
- **`"skill"`**: Routes to agents with specific skills or expertise
- **`"availability"`**: Assigns based on operator availability status

## 4. Example Usage

This example shows how to connect a user to support with proper error handling:

```
// 1. Gather user information first
input "ask_for_issue" {
    prompt = "Please describe your issue briefly so I can connect you with the right specialist."
    variable = "user_issue_description"
    next = "connect_to_support"
}

// 2. Connect to human agent using current implementation
connect "connect_to_support" {
    team_id = 123                                    // Technical support team ID
    priority = 5                                     // High priority assignment
    assignment_type = "round_robin"                  // Distribute evenly among agents
    assignment_by = "team"                          // Assign within the specified team
    operator_not_found = "no_agents_message"        // Handle no available operators
    operator_not_in_scheduler = "out_of_hours"      // Handle after-hours requests
    next_failed = "connection_failed"               // General failure handler
    next = "connection_successful"                  // Success handler
}

// 3. Success message
message "connection_successful" {
    type = text
    text = "You're now connected to a support specialist. They will help you with your issue."
    next = END
}

// 4. Handle no operators available
message "no_agents_message" {
    type = text
    text = "All our support agents are currently busy. You can wait in queue or leave your contact information for a callback."
    next = "offer_callback_options"
}

// 5. Handle operators out of schedule
message "out_of_hours" {
    type = text
    text = "Our support team is currently offline. Our business hours are Monday-Friday 9AM-6PM EST. Please try again during business hours or leave a message."
    next = "offer_callback_options"
}

// 6. Handle general connection failures
message "connection_failed" {
    type = text
    text = "We're experiencing technical difficulties connecting you to an agent. Please try again later or use our help center."
    next = "show_help_center_link"
}
```

## 5. Edge Generation

The connect block generates different types of edges based on the configured properties:

- **Success Edge**: Generated when `next` is provided - uses `sourceHandle: "success-JelouConnect:nodeId"`
- **Operator Not Found Edge**: Generated when `operator_not_found` is provided - uses `sourceHandle: "source-error-OPERATOR_NOT_FOUND:nodeId"`
- **Operator Not In Scheduler Edge**: Generated when `operator_not_in_scheduler` is provided - uses `sourceHandle: "source-error-OPERATORS_NOT_IN_SCHEDULER:nodeId"`
- **General Failure Edge**: Generated when `next_failed` is provided - uses `sourceHandle: "source-error-UNKNOWN_ERROR:nodeId"`

## 6. Error Handling

The connect block should always include comprehensive error handling paths:

- **No Operators Available** (`operator_not_found`): Provide alternative options like callbacks or help resources
- **Operators Out of Schedule** (`operator_not_in_scheduler`): Explain business hours and offer alternatives
- **General Connection Failures** (`next_failed`): Handle unknown errors with fallback options

## 7. Best Practices

- Always provide `operator_not_found` and `operator_not_in_scheduler` handlers with informative messages
- Use descriptive node IDs for error handling paths
- Consider providing callback options or alternative support channels in error handlers
- Set appropriate priority levels based on your support tier system
- Test assignment strategies to ensure optimal operator distribution
- Ensure all error handling nodes provide helpful information rather than using `END`
- Test connection flows during different hours and peak times to validate error handling