# Message Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `message` block is the primary way to send content to a user. Its behavior is determined by the `type` property, which can range from simple text to complex interactive elements like buttons, lists, and carousels.

**General Syntax:**

```hcl
message "unique_message_id" {
    type = <message_type>
    // ... properties specific to the message type ...
    next = "next_node_id" // Optional: Defines the next step
}
```

---

## 2. Message Types

### 2.1. `text`

Sends a plain text message.

- **Properties**:
  - `text` (Required): The content of the message. Can be a `QuotedString`, `TemplateLiteral`, or `Heredoc`. If you want to use triple doble quotation use Template Literal instead.
- **Example**:
  ```
  message "welcome_text" {
      type = text
      text = "Hello! Welcome to our service."
      next = "main_menu"
  }
  ```

### 2.2. Media Types: `image`, `video`, `audio`, `sticker`

Sends a media file.

- **Properties**:
  - `media_url` (Required): A public URL to the media file.
  - `caption` (Optional): Text that accompanies the media (not applicable to `audio` or `sticker`).
- **Example (`image`)**:
  ```
  message "promo_image" {
      type = image
      media_url = "[https://example.com/images/promo.png](https://example.com/images/promo.png)"
      caption = "Check out our latest promotion!"
      next = "ask_interest"
  }
  ```

### 2.3. `buttons`

Sends a message with interactive buttons. Properties are NOT separated by comma (",").

- **Channel Limitations**:
  - **WhatsApp**: Maximum of 3 buttons.
- **Properties**:
  - `text` (**Required**): The main message text.
  - `buttons` (Required): A list of button objects.
- **Button Object Structure**:
  Button Object Structure  properties are **NOT** separated by comma (",").
  - `id` (Required): A unique identifier for the button.
  - `title` (Required): The text displayed on the button.
  - `next` (Optional): The node to go to when this button is pressed.
  - `payload` (Optional): A data object to be processed.
    **Example**
    ```
    {
        id = "btn_balance"
        title = "Check Balance"
        next = "get_balance_flow"
    }
    ```
- **General Example**:
  ```
  message "main_menu_buttons" {
      type = buttons
      text = "What would you like to do?"
      buttons = [
          {
              id = "btn_balance"
              title = "Check Balance"
              next = "get_balance_flow"
          },
          {
              id = "btn_support"
              title = "Contact Support"
              next = "connect_to_agent"
          }
      ]
      next_expired = "session_timeout"
  }
  ```

### 2.4. `list`

Presents a vertical list of options to the user.

- **Channel Limitations**:

  - **WhatsApp**: Maximum of 11 options.
- **Properties**:

  - `text` (Required): The main message text.
  - `list_button_text` (Required): The text on the button that opens the list view.
  - `options` (Required): A list of option objects.
  - `option_not_found_message` (Required): Message to show if the user's response doesn't match an option.
- **Option Object Structure**:

  - `id`, `title`, `description`, `payload`, `next`.

  Option Object Structure  properties are **NOT** separated by comma (",").

  - `id` (Required): A unique identifier for the button.
  - `title` (Required): The text displayed on the button.
  - ``description``(Optional): The that explains the option object.
  - `payload` (Required): A data object to be processed, can be a empty map
  - `next` (Optional): The node to go to when this button is pressed.
    **Example**
    ```
    {
                id = "svc_1"
                title = "Account Services"
                description = "Manage your account
    details."
    	    payload = {} 
                next = "account_menu"
            }
    ```
- **General Example**:
- ```
  message "service_list" {
      type = list
      text = "Please choose a service:"
      list_button_text = "View Services"
      options = [
          {
              id = "svc_1"
              title = "Account Services"
              description = "Manage your account 
  details."
  	    payload = {}
              next = "account_menu"
          },
          {
              id = "svc_2"
              title = "Billing"
              description = "View invoices and payment history."
  	    payload = {}
              next = "billing_menu"
          }
      ]
      option_not_found_message = "Sorry, that's not a valid option."
  }
  ```

### 2.5. `numbered_list`

Sends a text message where each option is prefixed with a number for user selection.

- **Channel Limitations**:
  - **WhatsApp**: Maximum of 10 options.
- **Properties**:
  - `text` (Required): The introductory text.
  - `options` (Required): A list of option objects.
  - `option_not_found_message` (Required): Fallback message.
- **Example**:
  ```
  essage "product_selection_numbered" {
      type = numbered_list
      text = "Reply with the number of the product you're interested in:"
      options = [
          { id = "prod_a" title = "Laptop Pro" next = "laptop_details" },
          { id = "prod_b" title = "Wireless Mouse" next = "mouse_details" }
      ]
      option_not_found_message = "Please select a valid number."
      next_exit = "main_menu"
  }
  ```

### 2.6. `location`

Sends a geographical location.

- **Properties**:
  - `latitude` (Required): Latitude coordinate as a string (between -90 and 90).
  - `longitude` (Required): Longitude coordinate as a string (between -180 and 180).
- **Validation**: Up to 6 decimal places allowed for both coordinates.
- **Example**:
  ```
  message "office_location" {
      type = location
      latitude = "34.0522"
      longitude = "-118.2437"
      next = "confirm_location"
  }
  ```

### 2.7. `cta`

Sends a Call-To-Action message with a clickable URL.

- **Properties**:
  - `text` (Required): The main message text.
  - `cta_url` (Required): The URL to open when the button is clicked.
  - `cta_display_text` (Required): The text displayed on the CTA button.
- **Example**:
  ```
  message "learn_more_cta" {
      type = cta
      text = "Discover our new features!"
      cta_url = "https://example.com/features"
      cta_display_text = "Learn More"
      next = "follow_up"
  }
  ```

### 2.8. `carousel`

Sends a horizontal scrollable carousel with multiple cards.

- **Properties**:
  - `text` (Required): The main message text.
  - `title` (Optional): Title above the carousel.
  - `caption` (Optional): Caption below the carousel.
  - `options` (Required): List of carousel card objects.
  - `option_not_found_message` (Optional): Message when user selection is invalid.
  - `response_variable` (Optional): Variable to store the selected option.
  - `user_exited_the_menu` (Optional): Node to go to when user exits.
  - `is_blocking_enabled` (Optional): Whether to block other inputs.
  - `next_expired` (Optional): Node for timeout handling.
- **Carousel Card Object Structure**:
  ```
  {
      title = "Card Title"                     // Required
      subtitle = "Card Subtitle"               // Required
      media_url = "https://example.com/img.jpg" // Optional
      buttons = [                              // Required: List of button objects
          {
              id = "btn_id"
              title = "Button Text"
              payload = { key = "value" }
              next = "target_node"
          }
      ]
  }
  ```
- **Example**:
  ```
  message "product_carousel" {
      type = carousel
      text = "Choose from our featured products:"
      title = "Featured Products"
      options = [
          {
              title = "Smartphone Pro"
              subtitle = "Latest model with advanced features"
              media_url = "https://example.com/phone.jpg"
              buttons = [
                  {
                      id = "buy_phone"
                      title = "Buy Now"
                      next = "purchase_flow"
                  }
              ]
          }
      ]
      option_not_found_message = "Please select a valid option."
      next = "main_menu"
  }
  ```

### 2.9. `contacts`

Sends a contact card with contact information.

- **Properties**:
  - `data` (Required): Contact object with contact details.
- **Contact Object Structure**:
  ```
  {
      org = {                                          // Optional
          company = "Company Name"
          department = "Department Name"
      }
      name = {                                         // Optional
          formatted_name = "John Doe"
          first_name = "John"
          last_name = "Doe"
      }
      urls = [                                         // Optional
          { url = "https://example.com", type = "WORK" }
      ]
      emails = [                                       // Optional
          { email = "john@example.com", type = "WORK" }
      ]
      phones = [                                       // Optional
          { 
              phone = "+1234567890", 
              type = "WORK", 
              wa_id = "1234567890" 
          }
      ]
      addresses = [                                    // Optional
          {
              street = "123 Main St"
              city = "City"
              state = "State"
              zip = "12345"
              country = "Country"
              country_code = "US"
              type = "WORK"
          }
      ]
  }
  ```

### 2.10. `flow`

Sends a WhatsApp Flow message for interactive forms.

- **Properties**:
  - `text` (Required): The main message text.
  - `title` (Optional): Title above the flow.
  - `caption` (Optional): Caption below the flow.
  - `option_not_found_message` (Optional): Message for invalid responses.
  - `response_variable` (Optional): Variable to store flow response.
  - `flow` (Required): Flow configuration object.
  - `user_exited_the_menu` (Optional): Node when user exits.
  - `is_blocking_enabled` (Optional): Whether to block other inputs.
  - `next_expired` (Optional): Node for timeout handling.
- **Flow Object Structure**:
  ```
  {
      id = "flow_id_12345"                    // Required
      text_label_button = "Complete Form"     // Required
      name = "flow_name"                       // Required
      input_variable = "{{$memory.user_data}}" // Optional
      screen = "SCREEN_NAME"                   // Required
  }
  ```

### 2.11. `quick_reply`

Sends ephemeral buttons that disappear after being tapped.

- **Channel Limitations**:
  - **Facebook & Instagram only.**
- **Properties**:
  - `text` (Required): The main message text.
  - `options` (Required): A list of quick reply option objects.
- **Quick Reply Option Object Structure**:
  - `id`, `title`, `payload`, `next`.

### 2.12. Dynamic Options with `iterable`

For `buttons`, `list`, and `numbered_list`, you can dynamically generate options from a variable in memory.

- **How it works**:

  1. Add the `iterable` property to the message block, pointing to an array in memory (e.g., `iterable = "{{$memory.products}}"`).
  2. Define a single template object in the `options` or `buttons` list.
  3. Use `{{$item.property}}` syntax within the template to access data from each item in the array.
  4. **Important**: When using `iterable`, only one option/button template should be defined.
- **Example (`buttons` with `iterable`)**:

  ```
  // Assumes $memory.actions = [{id: "act1", label: "Action 1"}, {id: "act2", label: "Action 2"}]
  message "dynamic_actions" {
      type = buttons
      text = "Choose an action:"
      iterable = "{{$memory.actions}}"
      buttons = [
          {
              id = "dynamic_button" // ID becomes "dynamic-button" for all items
              title = "{{$item.label}}"
              payload = { action_id = "{{$item.id}}" }
              next = "process_action"
          }
      ]
  }
  ```
- **Example (`list` with `iterable`)**:

  ```
  message "dynamic_products" {
      type = list
      text = "Select a product:"
      list_button_text = "View Products"
      iterable = "{{$memory.products}}"
      options = [
          {
              id = "dynamic-button"  // Automatic ID for dynamic options
              title = "{{$item.name}}"
              description = "Price: {{$item.price}}"
              payload = { productId = "{{$item.id}}" }
              next = "product_details"
          }
      ]
      option_not_found_message = "Product not found."
  }
  ```

---

## 3. Advanced Properties

### 3.1. Flow Control Properties

All message types support these optional flow control properties:

- `next` - Default next node after message is processed
- `next_expired` - Node to go to if the message expires (timeout)
- `next_exit` - Node to go to if user exits from the message

### 3.2. Interactive Message Properties

For `buttons`, `list`, `numbered_list`, and `quick_reply` types:

- `is_blocking_enabled` (Optional, Boolean) - Prevents other inputs while waiting for response
- `expired_button_action` (Optional, Boolean) - Enables button expiration handling
- `one_time_use_buttons` (Optional, Boolean) - Buttons can only be used once
- `option_not_found_message` (Required for most) - Message when user input doesn't match options
- `expired_redirect_payload` (Optional) - Redirect configuration for expired interactions
- `redirect_payload` (Optional) - General redirect configuration

### 3.3. Redirect Payload Objects

Used for `expired_redirect_payload` and `redirect_payload`:

```
// Text redirect
expired_redirect_payload = {
    type = "text"
    text = "Session expired. Redirecting to main menu..."
}

// Workflow redirect
redirect_payload = {
    type = "workflow"
    workflowPath = "workflows/main_menu.wf"
}
```

### 3.4. Additional Properties by Type

**For `buttons` and `list`:**

- `title` (Optional) - Title above the message content
- `caption` (Optional) - Caption below the message content

**For media types (`image`, `video`):**

- `caption` (Optional) - Text caption for the media

---

## 4. Edge Generation

Different message types generate different types of edges for workflow navigation:

- **Standard messages**: Generate edges with `sourceHandle: nodeId`
- **Button/List options**: Generate edges with `sourceHandle: option.id` (or `"dynamic-button"` for iterable)
- **Exit actions**: Generate edges with `sourceHandle: "exit:nodeId"`
- **Expiration**: Generate edges with `sourceHandle: "expire:nodeId"`

---

## 5. Channel-Specific Limitations

| Message Type      | WhatsApp       | Facebook      | Instagram     | Web           |
| ----------------- | -------------- | ------------- | ------------- | ------------- |
| `buttons`       | Max 3          | No limit      | No limit      | No limit      |
| `list`          | Max 11 options | No limit      | No limit      | No limit      |
| `numbered_list` | Max 10 options | No limit      | No limit      | No limit      |
| `quick_reply`   | Not supported  | Supported     | Supported     | Not supported |
| `flow`          | Supported      | Not supported | Not supported | Not supported |

---

## 6. Best Practices

1. **Use appropriate message types**: Choose the right type based on the number of options and channel capabilities.
2. **Handle errors gracefully**: Always provide `option_not_found_message` for interactive messages.
3. **Consider timeouts**: Use `next_expired` for time-sensitive interactions.
4. **Validate coordinates**: For `location` type, ensure coordinates are within valid ranges.
5. **Test across channels**: Different channels may render messages differently.
6. **Optimize for mobile**: Keep text concise and buttons/options clear.
7. **Use dynamic options wisely**: Only define one template when using `iterable`.
