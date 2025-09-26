# Random Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `random` block randomly selects one path from a list of weighted routes. This is particularly useful for A/B testing, randomized user experiences, load balancing across different flows, or creating varied conversation experiences. Each route can have a weight that influences the probability of selection.

**General Syntax:**

```hcl
random "unique_random_id" {
    routes = [
        {
            id = "route_a"
            weight = 50
            next = "path_a"
        },
        {
            id = "route_b" 
            weight = 30
            next = "path_b"
        },
        {
            id = "route_c"
            weight = 20
            next = "path_c"
        }
    ]
}
```

## 2. Properties

- **`routes`** (Required): An array of route objects that define the possible paths and their selection weights.
- **`seed`** (Optional): A string used to seed the random number generator for reproducible results during testing.

## 3. Route Object Structure

Each route object contains:

- **`id`** (Required): A unique identifier for the route.
- **`weight`** (Required): A positive number (integer or decimal) representing the relative probability of selecting this route. Examples: `5`, `0.5`, `3.14`
- **`next`** (Required): The node ID to transition to if this route is selected.
- **`metadata`** (Optional): Additional data to store in memory when this route is selected.

## 4. Weight Distribution

Weights are relative, not percentages. The system calculates probabilities based on the total weight:

- Route A: weight 50 → 50/(50+30+20) = 50% probability
- Route B: weight 30 → 30/(50+30+20) = 30% probability  
- Route C: weight 20 → 20/(50+30+20) = 20% probability

You can also use decimal weights:
- Route A: weight 0.5 → 0.5/(0.5+0.3+0.2) = 50% probability
- Route B: weight 0.3 → 0.3/(0.5+0.3+0.2) = 30% probability
- Route C: weight 0.2 → 0.2/(0.5+0.3+0.2) = 20% probability

## 5. Example Usage

### 5.1. A/B Testing for Message Variations

This example randomly shows different welcome messages to test user engagement:

```hcl
// Random welcome message A/B test
random "welcome_message_test" {
    routes = [
        {
            id = "formal_welcome"
            weight = 50
            next = "formal_greeting"
            metadata = { test_variant = "formal", experiment_id = "welcome_test_v1" }
        },
        {
            id = "casual_welcome"
            weight = 50
            next = "casual_greeting" 
            metadata = { test_variant = "casual", experiment_id = "welcome_test_v1" }
        }
    ]
}

message "formal_greeting" {
    type = text
    text = "Good day! Welcome to our premium banking service. How may I assist you today?"
    next = "main_menu"
}

message "casual_greeting" {
    type = text
    text = "Hey there! =K Welcome to our banking app. What can I help you with?"
    next = "main_menu"
}
```

### 5.2. Load Balancing Between Service Channels

This example distributes users across different support channels:

```hcl
// Distribute support requests across channels
random "support_channel_router" {
    routes = [
        {
            id = "live_chat"
            weight = 40
            next = "connect_to_chat_agent"
        },
        {
            id = "phone_support"
            weight = 35
            next = "offer_phone_callback"
        },
        {
            id = "email_support"
            weight = 25
            next = "collect_email_inquiry"
        }
    ]
}

connect "connect_to_chat_agent" {
    department = "customer_support"
    priority = "medium"
    next = "chat_connected"
    next_failed = "chat_unavailable"
}

message "offer_phone_callback" {
    type = buttons
    text = "We can call you back within 15 minutes. Would you like to schedule a callback?"
    buttons = [
        { id = "yes_callback", title = "Yes, call me", next = "collect_phone_number" },
        { id = "no_callback", title = "No thanks", next = "main_menu" }
    ]
}
```

### 5.3. Randomized Promotional Content

This example shows different promotional offers with weighted distribution:

```hcl
// Show promotional content with different weights
random "promo_selector" {
    routes = [
        {
            id = "credit_card_promo"
            weight = 60  // Higher weight for main promotion
            next = "show_credit_card_offer"
            metadata = { promo_type = "credit_card", campaign_id = "cc_q1_2025" }
        },
        {
            id = "savings_promo"
            weight = 25
            next = "show_savings_offer"
            metadata = { promo_type = "savings", campaign_id = "savings_q1_2025" }
        },
        {
            id = "loan_promo"
            weight = 15
            next = "show_loan_offer"
            metadata = { promo_type = "loan", campaign_id = "loan_q1_2025" }
        }
    ]
}

// Example with decimal weights for fine-tuned distribution
random "promo_selector_v2" {
    routes = [
        {
            id = "premium_offer"
            weight = 0.75  // 75% probability
            next = "show_premium_offer"
            metadata = { tier = "premium", value = "high" }
        },
        {
            id = "standard_offer"
            weight = 0.25  // 25% probability
            next = "show_standard_offer"
            metadata = { tier = "standard", value = "medium" }
        }
    ]
}

message "show_credit_card_offer" {
    type = image
    media_url = "https://example.com/promos/credit-card-offer.jpg"
    caption = "<� Get 0% APR for 12 months on our premium credit card! Apply now and earn 50,000 bonus points."
    next = "credit_card_cta"
}
```

## 6. Testing and Reproducibility

Use the `seed` parameter for consistent results during testing:

```hcl
random "test_routing" {
    seed = "test_scenario_1"  // Same seed = same results
    routes = [
        { id = "path_1", weight = 50, next = "test_path_1" },
        { id = "path_2", weight = 50, next = "test_path_2" }
    ]
}
```

## 7. Analytics and Tracking

The selected route information is automatically stored in memory and can be accessed using `{{$memory.node_id}}` where `node_id` is the random block's ID.

```hcl
// The selected route information is automatically stored in memory
code "track_random_selection" {
    runtime = "javascript"
    code = `
        const selectedRoute = $memory.get('test_routing');
        $utils.logger.log('Random Route Selected', {
            route_id: selectedRoute.id,
            metadata: selectedRoute.metadata,
            timestamp: $utils.dayjs().toISOString()
        });
        
        return { tracked: true };
    `
    next = "continue_flow"
}

// You can also access it directly in message blocks
message "show_selected_route" {
    type = text
    text = "You were routed to {{$memory.test_routing.id}} variant"
    next = "continue"
}
```

## 8. Best Practices

- **Meaningful IDs**: Use descriptive route IDs for easier analytics and debugging
- **Metadata Tracking**: Include metadata for experiment tracking and analysis
- **Weight Adjustment**: Monitor performance and adjust weights based on results
- **Fallback Handling**: Ensure all routes lead to valid paths
- **Testing**: Use seeds during development and testing for predictable behavior
- **Documentation**: Document the purpose and expected behavior of each random distribution
- **Monitoring**: Track route selection patterns to verify distribution is working as expected