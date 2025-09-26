# Location Request Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `location_request` block prompts the user to share their device's geographical location. This is a specialized input type designed to handle coordinates, which can then be used for location-based services, delivery routing, or finding nearby points of interest.

### General Syntax

```hcl
location_request "unique_location_request_id" {
    prompt = "Please share your location so we can find nearby stores."
    variable = "user_location_data"
    next = "process_location_node"
    next_expired = "timeout_handler_node" // Optional
    next_exit = "exit_handler_node"       // Optional
}
```

## 2. Properties

- **`prompt`** (Required): The message displayed to the user, explaining why their location is needed. This can be a QuotedString, TemplateLiteral, or Heredoc. Should clearly explain the purpose to encourage user compliance.

- **`variable`** (Required): The name of the variable where the user's location data will be stored. The stored value will typically be an object containing latitude and longitude keys. Use descriptive names like `user_location` or `delivery_coords`.

- **`use_memory`** (Optional): Whether to store the location in memory for later use across the workflow. Defaults to false if not specified. When set to true, the location data persists and can be accessed in subsequent nodes using `{{$memory.variable_name}}`. Essential for workflows that reference location data multiple times.

- **`next`** (Optional): The node ID to transition to after the user successfully shares their location. If not specified, the workflow may default or end. Typically leads to location processing or API calls.

- **`next_expired`** (Optional): The node ID to transition to if the user does not respond to the location request within the configured time limit. Should provide alternative options or graceful fallback.

- **`next_exit`** (Optional): The node ID to transition to if the user explicitly denies the location sharing request. Should handle the denial gracefully and offer alternatives.

## 3. Use Cases

The `location_request` block is particularly useful for:

- **Delivery services**: Requesting customer location to calculate delivery fees and estimated arrival times
- **Emergency services**: Obtaining user location for emergency response and assistance
- **Location-based services**: Finding nearby stores, restaurants, or points of interest
- **Navigation applications**: Getting starting point coordinates for route planning
- **Service area validation**: Confirming users are within supported geographical regions
- **Geofencing**: Implementing location-based triggers and notifications

## 4. Example Usage

This example asks for the user's location to find nearby branches and handles cases where the user declines or doesn't respond.

```hcl
// 1. Ask the user to share their location
location_request "request_delivery_location" {
    prompt = "To calculate the delivery fee, please share your location."
    variable = "delivery_coords"
    next = "fetch_nearby_branches"
    next_expired = "handle_timeout"
    next_exit = "handle_location_denied"
}

// 2. Use the location data in an HTTP request
http "fetch_nearby_branches" {
    method = "GET"
    url = "https://api.example.com/branches?lat={{delivery_coords.latitude}}&lon={{delivery_coords.longitude}}"
    next = "display_branches"
    next_failed = "api_error_handler"
}

// 3. Inform the user if they denied the request
message "handle_location_denied" {
    type = text
    text = "We understand you prefer not to share your location. You can still browse our services, but we won't be able to show nearby branches or calculate delivery fees."
    next = "main_menu"
}
```

## 5. Advanced Example with Memory Usage

This example demonstrates using the `use_memory` property to persist location data across multiple workflow steps:

```hcl
// 1. Request location with memory persistence
location_request "capture_user_location" {
    prompt = "Please share your location to find nearby services and save your preferences."
    variable = "user_coordinates" 
    use_memory = true  // Persist location data in memory
    next = "process_location"
    next_expired = "location_timeout"
    next_exit = "location_denied"
}

// 2. Process the location data
code "process_location" {
    runtime = "javascript"
    code = `
        // Access the persisted location data
        const location = $memory.get('user_coordinates');
        
        // Perform location-based calculations
        const isServiceArea = checkServiceArea(location.latitude, location.longitude);
        
        // Store additional location metadata
        $memory.set('in_service_area', isServiceArea);
        $memory.set('user_city', getCityFromCoords(location.latitude, location.longitude));
        
        return { processed: true };
    `
    next = "show_location_results"
}

// 3. Later in the workflow, access the location data again
http "find_nearby_promotions" {
    method = "GET"
    url = "https://api.example.com/promotions?lat={{$memory.user_coordinates.latitude}}&lon={{$memory.user_coordinates.longitude}}&city={{$memory.user_city}}"
    next = "display_promotions"
    next_failed = "promotions_error"
}
