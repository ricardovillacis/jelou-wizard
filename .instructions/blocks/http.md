# HTTP Block Documentation

**Last Updated:** 2025-08-15

## 1. Overview

The `http` block allows the workflow to interact with external systems and APIs. It can be used to fetch data, send information, or trigger processes on other servers. The response from the HTTP request is automatically stored in the workflow’s context and can be accessed in subsequent nodes.

**Important runtime behavior:**

- The response is stored in `$context` under the name specified in the `output` property.
- If `output` is **not** specified, it defaults to `"response"`.
- To persist the response in `$memory`, you **must** explicitly map it in a `code` node.
- For **objects/arrays (JSON)**:

     ```javascript
     $memory.setJson("key", value, ttlInSeconds);
     ```

- For **primitive values**:

     ```javascript
     $memory.set("key", value);
     ```

- The **`ttl`** parameter in `setJson` is the time-to-live in seconds and defines how long the value remains in memory before expiring.

**General Syntax:**

```hcl
http "unique_http_request_id" {
    method = "GET"
    url = "[https://api.example.com/data](https://api.example.com/data)"
    headers = { "Authorization" = "Bearer ..." } // Optional
    params = { "query_param" = "value" }       // Optional
    body = { "key" = "value" }                 // Optional
    next = "success_handler_node"
    next_failed = "error_handler_node"         // Optional
}
```

## 2. Properties

- **`method`** (Required): The HTTP method for the request. Common values include "GET", "POST", "PUT", "PATCH", and "DELETE".
- **`url`** (Required): The endpoint URL for the API request. You can embed memory variables directly into the URL using `{{...}}` syntax (e.g., `url = "https://api.example.com/users/{{$memory.user_id}}"`).
- **`headers`** (Optional): An object containing key-value pairs for HTTP request headers, such as for authentication (Authorization) or content type (Content-Type). Supports template variables with `{{...}}` syntax.
- **`params`** (Optional): An object containing key-value pairs that will be appended to the URL as query string parameters. Supports template variables with `{{...}}` syntax.
- **`body`** (Optional): An object representing the payload for POST, PUT, or PATCH requests. This object will be automatically converted to a JSON string. Supports template variables with `{{...}}` syntax.
- **`authentication`** (Optional): An object for HTTP authentication. Structure: `{ type = "basic", user = "username", pass = "password" }`. Currently supports basic authentication.
- **`output`**  (Optional): Name used to store the HTTP response in $context. If not specified, defaults to "response". Retrieve it later with: `$context.getHttpResponse("output_name");` in node code
- **`timeout`** (Optional): Request timeout in seconds (Integer). Default behavior applies if not specified.
- **`retry_attempts`** (Optional): Number of retry attempts for failed requests (Integer). Default is no retries if not specified.
- **`retry_delay`** (Optional): Delay between retry attempts in seconds (Integer). Only applicable when `retry_attempts` is set.
- **`ssl_verify`** (Optional): Whether to verify SSL certificates (Boolean). Default is `true`.
- **`next`** (Required): The node ID to transition to after the HTTP request completes successfully (i.e., returns a 2xx status code).
- **`next_failed`** (Optional): The node ID to transition to if the request fails (e.g., network error, non-2xx status code, timeout, authentication failure). This is crucial for robust error handling.

## 3. Example Usage

This example shows how to fetch weather data for a ZIP code provided by the user and then display it.

```hcl
// 1. Get the user's ZIP code
input "ask_for_zip" {
    prompt = "Please enter your ZIP code to get the weather forecast."
    variable = "zip_code"
    next = "get_weather_data"
}

// 2. Call weather API with custom output
http "get_weather_data" {
    method = "GET"
    url    = "https://api.weather.com/forecast"
    output = "weather_api_response" // The output property should always be placed after the headers property
    params = {
        zip   = "{{$memory.zip_code}}",
        apiKey = "{{$env.WEATHER_API_KEY}}"
    }
    next        = "map_weather_data"
    next_failed = "handle_api_error"
}

// 3. Map from $context → $memory
code "map_weather_data" {
    runtime = "javascript"
    code = `
        const response = $context.getHttpResponse("weather_api_response").json();
        $memory.setJson("weather_data", response, 300);
        $memory.set("temperature", response?.temperature ?? null);
        $memory.set("conditions",  response?.conditions ?? "");
    `
    next = "display_weather"
}

// 4. Show result
message "display_weather" {
    type = text
    text = "The current temperature for your area is {{$memory.temperature}}°F with {{$memory.conditions}}."
    next = END
}

// 5. Handle potential API errors
message "handle_api_error" {
    type = text
    text = "Sorry, I couldn't retrieve the weather forecast at this time. Please try again later."
    next = END
}
```

## 4. Response Storage and Access

When an HTTP request completes successfully:

- The full response is stored in $context under the key specified by output or "response" by default.

- Access it with:

    ```javascript
    const response = $context.getHttpResponse("output_name"); // or "response"
    const request  = $context.getHttpRequest("output_name");
    ```

  - JSON body:

    ```javascript
    const dataObj = response.json();
    ```

  - Status code:

    ```javascript
    const dataObj = response.status();
    ```

### Moving to $memory

- Object/Array (JSON) with TTL:

    ```javascript
    $memory.setJson("my_key", dataObj, 600);
    ```

- Primitive:

    ```javascript
    $memory.set("my_key", "value");
    ```

### Response Structure

The stored response typically includes:

- Response body (parsed as JSON if applicable)
- Status code
- Headers

## 5. Template Variables and Environment Variables

All HTTP block properties support template variable interpolation using `{{...}}` syntax:

### Memory Variables

```hcl
http "dynamic_request" {
    method = "POST"
    url = "https://api.example.com/users/{{$memory.user_id}}/profile"
    headers = {
        "Authorization" = "Bearer {{$memory.access_token}}",
        "X-User-Agent" = "MyApp/{{$memory.app_version}}"
    }
    params = {
        "include" = "{{$memory.include_fields}}",
        "format" = "json"
    }
    body = {
        "user_data" = "{{$memory.user_input}}",
        "timestamp" = "{{$memory.current_time}}"
    }
    next = "process_response"
}
```

### Environment Variables

Access environment variables using the `{{$env.VARIABLE_NAME}}` syntax:

```hcl
http "secure_api_call" {
    method = "GET"
    url = "https://secure-api.example.com/data"
    headers = {
        "Authorization" = "Bearer {{$env.API_TOKEN}}",
        "X-API-Key" = "{{$env.SECRET_API_KEY}}"
    }
    params = {
        "client_id" = "{{$env.CLIENT_ID}}"
    }
    next = "handle_response"
}
```

## 6. Advanced Configuration Examples

### Authentication Example

```hcl
http "authenticated_request" {
    method = "GET"
    url = "https://api.example.com/protected-data"
    auth = {
        type = "basic",
        user = "{{$env.API_USERNAME}}",
        pass = "{{$env.API_PASSWORD}}"
    }
    next = "process_data"
    next_failed = "auth_error"
}
```

### Retry and Timeout Configuration

```hcl
http "resilient_api_call" {
    method = "POST"
    url = "https://unreliable-api.example.com/data"
    body = { "request_data" = "{{$memory.user_data}}" }
    timeout = 30
    retry_attempts = 3
    retry_delay = 5
    ssl_verify = true
    next = "success_handler"
    next_failed = "final_error_handler"
}
```

## 7. Error Handling

The `next_failed` path is triggered in several scenarios:

- Network connectivity issues
- HTTP status codes outside the 2xx range (client errors 4xx, server errors 5xx)
- Request timeouts
- Authentication failures
- SSL certificate verification failures (when `ssl_verify = true`)
- Maximum retry attempts exceeded

### Comprehensive Error Handling

```hcl
http "robust_api_call" {
    method = "GET"
    url = "https://api.example.com/data"
    timeout = 15
    retry_attempts = 2
    retry_delay = 3
    next = "success_path"
    next_failed = "error_analysis"
}

// Handle different types of errors
code "error_analysis" {
    runtime = "javascript"
    code = `
        const httpResponse = $context.getHttpResponse('response');
        const statusCode = httpResponse?.status;
        
        if (statusCode >= 400 && statusCode < 500) {
            $memory.set('error_type', 'client_error');
        } else if (statusCode >= 500) {
            $memory.set('error_type', 'server_error');
        } else {
            $memory.set('error_type', 'network_error');
        }
    `
    next = "handle_specific_error"
}
```
