# Package Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `package` block executes pre-built Marketplace Skills within your workflow. These are reusable components that encapsulate common functionality like data validation, integrations with third-party services, or complex business logic. Packages help reduce development time and ensure consistency across workflows.

**General Syntax:**

```
package "unique_package_id" {
    use = "@jelou/email_validator:1.2.0"           // (Required; QuotedString – package identifier in the form @companySlug/packageName:version. The :version part is optional; latest is used when omitted)
    inputs = {                                   // (Required; RecursiveObject – input map)
        email = { type = "STRING" value = "{{$memory.user_email}}" },
        strict_mode = { type = "BOOLEAN" value = "true" }
    }
    variable = "validation_result"                // (Optional; QuotedString – where to store the package response)
    next = "process_validation"                   // (Optional; QuotedString or END)
    next_failed = "handle_package_error"          // (Optional; QuotedString or END)
}
```

## 2. Properties

- **`use`** (Required): Identifier of the package to execute in the form `"@companySlug/packageName:version"` (QuotedString). The `:version` part is optional; latest is used when omitted.
- **`inputs`** (Required): A map of inputs for the package (RecursiveObject). Each entry must contain **`type`** (one of `STRING`, `NUMBER`, `BOOLEAN`, `ARRAY`, `ENUM`, `OBJECT`) and **`value`** (QuotedString or TemplateLiteral) .**IMPORTANT** a map can be empy(if no params wants to be sent).
  **Example**
  ```
      inputs = {
        provider = { type = "STRING" value = "POCKET" },
        environment = { type = "STRING" value = "DEV" },
        currency = { type = "STRING" value = "USD" },
        tax_rate = { type = "NUMBER" value = "15" },
        payment_type = { type = "STRING" value = "PAYMENT" }
      }
  ```
- **`variable`** (Optional): Variable name where the package's response will be saved (QuotedString).
- **`next`** (Optional): Path to follow when the package execution finishes successfully (QuotedString or END).
- **`next_failed`** (Optional): Path to follow when the package execution fails (QuotedString or END).

## 3. Edge Generation

The package block generates edges based on the configured properties:

- **Success Edge**: Generated when `next` is provided – uses `sourceHandle: "success-<nodeId>"`
- **Failure Edge**: Generated when `next_failed` is provided – uses `sourceHandle: "source-error-<nodeId>"`

## 4. Common Marketplace Packages

### 4.1. Data Validation Packages

- **`email_validator`**: Validates email addresses with various options
- **`phone_validator`**: Validates and formats phone numbers
- **`credit_card_validator`**: Validates credit card numbers and types
- **`address_validator`**: Validates and standardizes addresses

### 4.2. Integration Packages

- **`salesforce_lookup`**: Query Salesforce records
- **`stripe_payment`**: Process payments through Stripe
- **`sendgrid_email`**: Send emails via SendGrid
- **`twilio_sms`**: Send SMS messages through Twilio

### 4.3. Utility Packages

- **`date_calculator`**: Perform date arithmetic and formatting
- **`currency_converter`**: Convert between currencies
- **`text_analyzer`**: Analyze text sentiment and extract entities
- **`qr_generator`**: Generate QR codes

## 5. Input/Output Handling

### 5.1. Input Mapping

Packages receive inputs through the `inputs` object, each input structured is separated by a comma BUT properties inside object structure is NOT separated by comma. Each package has a specific schema:

```
package "validate_user_data" {
    use = "@jelou/comprehensive_validator:2.1.0"
    inputs = {
        email = { type = "STRING" value = "{{$memory.user_email}}" },
        phone = { type = "STRING" value = "{{$memory.user_phone}}" },
        validation_level = { type = "STRING" value = "strict" },
        country_code = { type = "STRING" value = "US" }
    }
    variable = "user_data_validation"
    next = "check_validation_results"
}
```

### 5.2. Output Structure

Package outputs are typically structured objects:

```json
{
    "success": true,
    "results": {
        "email": {
            "valid": true,
            "formatted": "user@example.com",
            "provider": "gmail"
        },
        "phone": {
            "valid": true,
            "formatted": "+1-555-123-4567",
            "country": "US"
        }
    },
    "metadata": {
        "execution_time": 150,
        "package_version": "2.1.0"
    }
}
```

## 6. Example Usage

This example demonstrates using multiple packages in sequence for user registration validation.

```
// 1. Collect user information
input "collect_email" {
    prompt = "Please enter your email address:"
    variable = "user_email"
    next = "collect_phone"
}

input "collect_phone" {
    prompt = "Please enter your phone number:"
    variable = "user_phone"
    next = "validate_user_data"
}

// 2. Validate email and phone using a package
package "validate_user_data" {
    use = "@jelou/multi_field_validator:2.1.0"
    inputs = {
        fields = { type = "OBJECT" value = "{{$memory.user_fields}}" },
        email = { type = "STRING" value = "{{$memory.user_email}}" },
        phone = { type = "STRING" value = "{{$memory.user_phone}}" },
        country = { type = "STRING" value = "US" },
        strict_validation = { type = "BOOLEAN" value = "true" }
    }
    variable = "validation_results"
    next = "process_validation"
    next_failed = "validation_error"
}

// 3. Process validation results
conditional "process_validation" {
    conditions = [
        {
            id = "all_valid"
            terms = [
                { operator = "equal", value1 = "{{$memory.validation_results.email.valid}}", value2 = true },
                { operator = "equal", value1 = "{{$memory.validation_results.phone.valid}}", value2 = true }
            ]
            next = "create_user_account"
        }
    ]
    next = "show_validation_errors"
}

// 4. Create account using another package
package "create_account" {
    use = "@jelou/user_registration:1.5.0"
    inputs = {
        email = { type = "STRING" value = "{{$memory.validation_results.email.formatted}}" },
        phone = { type = "STRING" value = "{{$memory.validation_results.phone.formatted}}" },
        source = { type = "STRING" value = "chatbot_registration" }
    }
    variable = "account_creation_result"
    next = "registration_success"
    next_failed = "registration_failed"
}

message "registration_success" {
    type = text
    text = "Account created successfully! Your user ID is {{$memory.account_creation_result.user_id}}."
    next = END
}
```

## 7. Error Handling

Always implement comprehensive error handling for package executions:

```
message "validation_error" {
    type = text
    text = "Sorry, there was an error validating your information. Please try again."
    next = "collect_email"
}

message "registration_failed" {
    type = text
    text = "Account creation failed. Please contact support or try again later."
    next = "offer_support_contact"
}
```

## 8. Best Practices

- **Version Specification**: Include version numbers in the `use` property for production workflows to ensure consistency (e.g., `@jelou/package:1.2.0`)
- **Input Validation**: Validate inputs before passing them to packages
- **Error Handling**: Always include `next_failed` paths for robust error handling
- **Input Type Specification**: Always specify the correct `type` for each input parameter (`STRING`, `NUMBER`, `BOOLEAN`, `ARRAY`, `ENUM`, `OBJECT`)
- **Testing**: Test package integrations thoroughly in development environments
- **Documentation**: Keep track of package dependencies and their input/output schemas
- **Monitoring**: Monitor package execution times and failure rates in production
