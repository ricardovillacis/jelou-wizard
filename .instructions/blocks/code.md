# Code Block Documentation

**Last Updated:** 2025-08-04

## 1. Overview

The `code` block allows you to execute custom JavaScript code within a secure, sandboxed environment. It is a powerful tool for performing complex logic that isn't covered by other block types, such as data validation, transformations, calculations, or dynamic variable manipulation. Results should be stored in memory using the available memory APIs for use in subsequent nodes.

**General Syntax:**

```hcl
code "unique_code_block_id" {
    runtime = "javascript"
    code = \`
        // Your JavaScript code here
        const result = 1 + 1;
        $memory.set('sum', result);
    \`
    next = "success_handler_node"
    next_failed = "error_handler_node" // Optional
}
```

## 2. Properties

- **`runtime`** (Required): Specifies the execution engine. Currently, the only supported value is "javascript".
- **`code`** (Conditional): An inline script to be executed, provided as a TemplateLiteral or Heredoc. This is the most common way to use the block for short to medium-sized scripts.
- **`file`** (Conditional): The path to an external .js or .jsw file containing the script to be executed. This is useful for longer, more complex, or reusable code.

**Note:** You must provide either the `code` or `file` property, but not both.

- **`next`** (Required): The node ID to transition to after the script executes successfully.
- **`next_failed`** (Optional): The node ID to transition to if the script throws an error during execution. This is essential for robust error handling.

## 2.1. External File Usage

The `file` property allows you to reference external JavaScript files, providing better code organization and reusability. This approach is recommended for:

- Complex logic that benefits from syntax highlighting and IDE support
- Reusable code across multiple workflows
- Better code organization and maintainability
- Code that requires external tooling (linting, formatting, etc.)
- **Code blocks exceeding 5 lines** - Should be extracted to maintain readability and organization

**Supported File Extensions:**

- `.js` - Standard JavaScript files
- `.jsw` - Workflow-specific JavaScript files

**File Resolution:**

- Files are resolved relative to the workflow file location
- The compiler automatically reads and inlines the file content during compilation
- Files are processed at compile time, not runtime

### When to Extract Code to External Files

**Extract code when:**

- The inline code exceeds 5 lines of logic
- The code contains any functions or complex operations
- The same logic is used across multiple workflows
- The code requires commenting or documentation
- You need proper IDE support for debugging and development

**Keep inline when:**

- The code is 5 lines or less
- Simple one-line operations or assignments
- Basic return statements or simple conditionals

**Example with External File:**

```hcl
// Workflow file: workflows/onboarding/user-registration.wf
code "validate_user_data" {
    runtime = "javascript"
    file = "scripts/user-validation.js"  // Resolves to workflows/onboarding/scripts/user-validation.js
    next = "process_validation_result"
    next_failed = "validation_error"
}
```

**Code Extraction Example:**

When your code exceeds 5 lines, extract it:

```hcl
// ❌ AVOID: Inline code longer than 5 lines
code "validate_email" {
    runtime = "javascript"
    code = `
        const email = $memory.get('user_email');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);
        $memory.set('email_valid', isValid);
        $utils.logger.log('Email Validation', { email, isValid });
        return { isValid };
        // 6+ lines - should be extracted!
    `
    next = "display_results"
}

// ✅ BETTER: Extract to external file
code "validate_email" {
    runtime = "javascript"
    file = "scripts/email-validation.js"
    next = "display_results"
    next_failed = "validation_error"
}

// ✅ ACCEPTABLE: Inline code of 5 lines or less
code "simple_calculation" {
    runtime = "javascript"
    code = `
        const value = $memory.get('input_value');
        const result = value * 2;
        $memory.set('calculation_result', result);
    `
    next = "show_result"
}
```

**Example External File (`scripts/user-validation.js`):**

```javascript
// User data validation logic
const userData = $context.getJson('user_form_data');

// Validate required fields
const requiredFields = ['name', 'email', 'phone'];
const missingFields = requiredFields.filter(field => !userData[field]);

if (missingFields.length > 0) {
    $memory.set('validation_errors', missingFields);
    $memory.setJson('validation_result', { 
        valid: false, 
        errors: missingFields,
        message: `Missing required fields: ${missingFields.join(', ')}`
    }, 3600);
    // Use next_failed to handle validation failure
}

// Validate email format
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(userData.email)) {
    $memory.setJson('validation_result', { 
        valid: false, 
        errors: ['email'],
        message: 'Invalid email format'
    }, 3600);
    // Use next_failed to handle validation failure
}

// Validate phone format (basic example)
const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
if (!phoneRegex.test(userData.phone)) {
    $memory.setJson('validation_result', { 
        valid: false, 
        errors: ['phone'],
        message: 'Invalid phone format'
    }, 3600);
    // Use next_failed to handle validation failure
}

// All validations passed
$memory.setJson('validated_user_data', userData, 100);
$memory.setJson('validation_result', { 
    valid: true, 
    message: 'All validations passed'
}, 3600);
```

## 3. Execution Context & Available APIs

Your script runs in an environment with access to several pre-defined global objects and utility libraries, allowing it to interact with the workflow's state.

### 3.1. State Management

**`$memory`**: Interact with the user's session memory.

#### Primitives

- **`$memory.set(key, value, [TTL])`** — Stores a primitive (`string`, `number`, `boolean`). TTL optional, max 2,628,000 seconds. Throws error if value is JSON.
- **`$memory.get(key, [defaultValue])`** — Retrieves a primitive. If not found and `defaultValue` provided, returns it; otherwise, throws error.

#### JSON (objects/arrays)

- **`$memory.setJson(key, value, TTL)`** — Stores a JSON. TTL required, max 86,400 seconds. Throws error if value is primitive.
- **`$memory.getJson(key, [defaultJSON])`** — Retrieves JSON. If not found and `defaultJSON` provided, returns it; otherwise, throws error.

#### Files

- **`await $memory.setFile(key, value, TTL, type)`** — Uploads file (base64, raw, or JSON) with MIME type. TTL required, max 604,800 seconds.

**Allowed types:**

- Text: `text/plain`
- JSON: `application/json`
- XML: `application/xml`, `text/xml`
- Images: `image/jpeg`, `image/png`, `image/gif`
- Video: `video/mp4`, `video/webm`, `video/ogg`, `video/x-msvideo`, `video/mpeg`
- Audio: `audio/mpeg`, `audio/wav`, `audio/ogg`, `audio/aac`, `audio/flac`
- Docs: `application/pdf`

**File retrieval methods:**

- `.toUrl()` — Returns public S3 URL (sync)
- `await .toBase64()` — Returns base64 content (async)
- `await .toRaw()` — Returns raw content (async)

#### Delete

- **`$memory.delete(key)`** — Deletes one or multiple keys.

### 3.2. Context Access

**`$context`**: Access data from the current execution context, such as HTTP responses.

- `$context.get(key, [defaultValue])`
- `$context.set(key, value)`
- `$context.getHttpResponse(nodeId)`: Gets the full response from a previous http block.

### 3.3. User/Company Data

- `$user.get(key)` — Read-only
- `$bot.get(key)` — Read-only
- `$company.get(key)` — Read-only

### 3.4. Environment Variables

- `$env.get(key, [defaultValue])` — Secure access to secrets

### 3.5. Input/Output Context (Tool/Marketplace Skills)

- **`$input`**: Access inputs declared in the Start node for Tool or Marketplace skill contexts.
  - `$input.get(key, [defaultValue])`
- **`$output`**: Set values to outputs (Nodes) declared in the canvas of a tool or Marketplace Skill.
  - `$output.set(key, value)`

### 3.3. Utilities ($utils)

#### Date and Time Manipulation

- **`$utils.dayjs`**: Day.js library for parsing, validating, manipulating, and displaying dates and times.
  - `$utils.dayjs().format(formatString)` - Format current date/time
  - `$utils.dayjs().add(value, unit)` - Add time (e.g., `add(7, 'day')`)
  - `$utils.dayjs().subtract(value, unit)` - Subtract time
  - `$utils.dayjs().diff(date, unit, [float])` - Calculate difference between dates
  - `$utils.dayjs().startOf(unit)` - Start of time unit (e.g., `startOf('day')`)
  - `$utils.dayjs().endOf(unit)` - End of time unit
  - `$utils.dayjs().isBefore(date)` - Check if before another date
  - `$utils.dayjs().isAfter(date)` - Check if after another date
  - `$utils.dayjs().isSame(date, unit)` - Check if same as another date
  - Example: `$utils.dayjs().add(7, 'day').format('YYYY-MM-DD')`

#### Data Manipulation

- **`$utils._`**: Lodash library for advanced data manipulation (arrays, objects, etc.).
  - `$utils._.chunk(array, size)` - Create chunks from array
  - `$utils._.debounce(func, wait)` - Debounce function calls
  - `$utils._.cloneDeep(value)` - Deep clone objects/arrays
  - `$utils._.merge(object, sources)` - Deep merge objects
  - `$utils._.get(object, path, [defaultValue])` - Safe property access
  - `$utils._.uniq(array)` - Remove duplicates from array
  - `$utils._.filter(collection, predicate)` - Filter collection
  - `$utils._.map(collection, iteratee)` - Transform collection
  - Example: `$utils._.get(myObject, 'a.b.c', 'default')`

#### Cryptographic Functions

- **`$utils.crypto`**: Standard cryptographic functions for hashing, encryption, and security.
  - `$utils.crypto.createHash(algorithm)` - Create hash (e.g., 'sha256', 'md5')
  - `$utils.crypto.createHmac(algorithm, key)` - Create HMAC
  - `$utils.crypto.randomBytes(size)` - Generate random bytes
  - `$utils.crypto.pbkdf2(password, salt, iterations, keylen, digest)` - Key derivation
  - `$utils.crypto.createCipheriv(algorithm, key, iv)` - Create cipher for encryption
  - `$utils.crypto.createDecipheriv(algorithm, key, iv)` - Create decipher for decryption
  - `$utils.crypto.generateKeyPair(type, options, callback)` - Generate public/private key pairs
  - `$utils.crypto.sign(algorithm, data, privateKey)` - Digital signature creation
  - `$utils.crypto.verify(algorithm, data, publicKey, signature)` - Signature verification
  - Example: `$utils.crypto.createHash('sha256').update(data).digest('hex')`

#### URL Shortening

- **`$utils.shortly`**: Functions to generate short URLs.
  - `$utils.shortly.create(longUrl, tags, options)` - Create short URL
  - `$utils.shortly.get(shortCode)` - Retrieve original URL from short code

#### Logging and Debugging

- **`$utils.logger`**: Log data for debugging and monitoring purposes.
  - `$utils.logger.log(key, value)` - Log key-value pairs for debugging

## 4. Example Usage

### 4.1. Data Validation Example

This example validates a user-provided email address and sets a flag in memory based on the result.

```hcl
// 1. Get the user's email
input "ask_for_email" {
    prompt = "Please provide your email address:"
    variable = "user_email_input"
    next = "validate_email_with_code"
}

// 2. Use a code block to validate the format
code "validate_email_with_code" {
    runtime = "javascript"
    code = \`
        const email = $memory.get('user_email_input', '');
        
        // Simple regex for email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);

        $utils.logger.log('Email Validation', { email: email, valid: isValid });

        // Store the result in memory, accessible via
        // {{$memory.email_is_valid}}
        $memory.set('email_is_valid', isValid);
    \`
    next = "check_validation_result"
    next_failed = "handle_code_error"
}

// 3. Use a conditional block to act on the result
conditional "check_validation_result" {
    conditions = [
        {
            id = "rule_is_valid"
            terms = [{ 
                operator = "equal", 
                value1 = "{{$memory.email_is_valid}}", 
                value2 = true 
            }]
            next = "success_message"
        }
    ]
    next = "failure_message" // Default path if not valid
}

message "success_message" {
    type = text
    text = "Thank you, your email is valid!"
    next = END
}

message "failure_message" {
    type = text
    text = "The email format appears to be incorrect. Let's try again."
    next = "ask_for_email"
}
```

### 4.2. Data Transformation Example

Transform API response data and calculate derived values:

```hcl
// After receiving data from an HTTP block
code "transform_user_profile" {
    runtime = "javascript"
    code = `
        const TTL_1H = 3600;
        const apiResponse = $context.getHttpResponse('fetch_user_api');
        const userData = apiResponse.data;
        
        // Transform and enrich user data
        const transformedData = {
            fullName: userData.first_name + ' ' + userData.last_name,
            age: $utils.dayjs().diff(userData.birth_date, 'year'),
            initials: userData.first_name.charAt(0) + userData.last_name.charAt(0),
            isAdult: $utils.dayjs().diff(userData.birth_date, 'year') >= 18,
            accountAge: $utils.dayjs().diff(userData.created_at, 'day'),
            preferences: $utils._.pick(userData, ['theme', 'language', 'notifications'])
        };
        
        // JSON → setJson (TTL required)
        $memory.setJson('user_profile', transformedData, TTL_1H);
        
        $utils.logger.log('User Profile Transformation', {
            originalData: userData,
            transformedData: transformedData
        });
    `
    next = "display_profile"
    next_failed = "transformation_error"
}
```

### 4.3. Complex Calculation Example

Calculate financial metrics and scoring:

```hcl
code "calculate_credit_score" {
    runtime = "javascript"
    code = `
        const TTL_1H = 3600;
         // These are JSON containers → use getJson with defaults
        const transactions = $memory.getJson('user_transactions', []);
        const accountInfo = $memory.getJson('account_info', {});
        // Calculate financial metrics
        const totalIncome = $utils._.sumBy(
            $utils._.filter(transactions, t => t.type === 'income'), 
            'amount'
        );
        
        const totalExpenses = $utils._.sumBy(
            $utils._.filter(transactions, t => t.type === 'expense'), 
            'amount'
        );
        
        const monthlyAverage = totalIncome / 12;
        const savingsRate = ((totalIncome - totalExpenses) / totalIncome) * 100;
        
        // Calculate credit score factors
        let creditScore = 300; // Base score
        
        // Payment history (40% of score)
        const latePayments = $utils._.filter(transactions, t => t.late_payment).length;
        creditScore += Math.max(0, (100 - latePayments * 10)) * 2.8;
        
        // Credit utilization (30% of score)
        const utilizationRate = accountInfo.current_balance / accountInfo.credit_limit;
        if (utilizationRate < 0.1) creditScore += 210;
        else if (utilizationRate < 0.3) creditScore += 150;
        else creditScore += Math.max(0, 150 - (utilizationRate * 100));
        
        // Length of credit history (15% of score)
        const accountAgeMonths = $utils.dayjs().diff(accountInfo.opened_date, 'month');
        creditScore += Math.min(105, accountAgeMonths * 2);
        
        // Round to nearest 5
        creditScore = Math.round(creditScore / 5) * 5;
        
        const result = {
            creditScore: Math.min(850, Math.max(300, creditScore)),
            metrics: {
                monthlyIncome: monthlyAverage,
                savingsRate: Math.round(savingsRate * 100) / 100,
                utilizationRate: Math.round(utilizationRate * 10000) / 100,
                accountAgeMonths: accountAgeMonths
            },
            recommendations: []
        };
        
        // Generate recommendations
        if (savingsRate < 10) {
            result.recommendations.push("Consider increasing your savings rate to at least 10%");
        }
        if (utilizationRate > 0.3) {
            result.recommendations.push("Try to keep credit utilization below 30%");
        }
        
        // JSON → setJson (TTL required)
        $memory.setJson('credit_analysis', result, TTL_1H);
    `
    next = "display_credit_report"
    next_failed = "calculation_error"
}
```

### 4.4. Dynamic Content Generation Example

Generate personalized content based on user data and preferences:

```hcl
code "generate_personalized_content" {
    runtime = "javascript"
    file = "scripts/content-generator.js"
    next = "send_personalized_message"
    next_failed = "content_generation_error"
}
```

**External file (`scripts/content-generator.js`):**

```javascript
const TTL_1H = 3600;
const userProfile = $memory.getJson('user_profile', {});
const preferences = $memory.getJson('user_preferences', {});
const currentTime = $utils.dayjs();

// Determine greeting based on time of day
let greeting;
const hour = currentTime.hour();
if (hour < 12) greeting = "Good morning";
else if (hour < 18) greeting = "Good afternoon";
else greeting = "Good evening";

// Generate personalized content based on user data
const personalizedContent = {
    greeting: `${greeting}, ${userProfile.firstName}!`,
    mainMessage: generateMainMessage(userProfile, preferences),
    recommendations: generateRecommendations(userProfile),
    nextSteps: generateNextSteps(userProfile.accountType, preferences)
};

function generateMainMessage(profile, prefs) {
    const templates = {
        premium: `As a premium member, you have access to exclusive features that can help maximize your ${profile.primaryGoal}.`,
        standard: `Your ${profile.accountType} account gives you access to our core features for ${profile.primaryGoal}.`,
        basic: `Getting started with ${profile.primaryGoal}? Your basic account is perfect for learning the fundamentals.`
    };
    
    return templates[profile.accountType] || templates.basic;
}

function generateRecommendations(profile) {
    const recommendations = [];
    
    if (profile.lastLoginDays > 7) {
        recommendations.push("Welcome back! Check out the new features we've added since your last visit.");
    }
    
    if (profile.completedTasks < 3) {
        recommendations.push("Complete your profile setup to unlock more personalized recommendations.");
    }
    
    if (profile.accountType === 'basic' && profile.engagementScore > 80) {
        recommendations.push("You're very active! Consider upgrading to premium for advanced features.");
    }
    
    return recommendations;
}

function generateNextSteps(accountType, preferences) {
    const steps = {
        premium: [
            "Explore your advanced analytics dashboard",
            "Set up automated workflows",
            "Join our premium community forum"
        ],
        standard: [
            "Complete your weekly goals",
            "Try our new collaboration features",
            "Review your progress reports"
        ],
        basic: [
            "Complete your profile",
            "Take the getting started tour",
            "Connect with our community"
        ]
    };
    
    return $utils._.shuffle(steps[accountType] || steps.basic).slice(0, 2);
}

// Store generated content (JSON → setJson)
$memory.setJson('personalized_content', personalizedContent, TTL_1H);

$utils.logger.log('Content Generation', {
    userId: userProfile.id,
    contentType: 'personalized_welcome',
    timestamp: currentTime.toISOString()
});
```

## 5. Best Practices

### 5.1. Code Organization

**Choose the Right Approach:**

- **Inline Code**: Use only for very simple scripts (5 lines or less) with basic operations
- **External Files**: Use for any code exceeding 5 lines, reusable functions, or code that benefits from IDE support

**Recommended File Organization:**

Scripts should be organized in a `scripts` folder within the same directory as your workflow files. This keeps all workflow-related code together and makes maintenance easier.

```
workflow-project/
├── workflows/
│   ├── customer-support/
│   │   ├── main.wf
│   │   └── scripts/
│   │       ├── ticket-validation.js
│   │       ├── priority-calculation.js
│   │       └── response-generator.js
│   ├── onboarding/
│   │   ├── onboarding.wf
│   │   └── scripts/
│   │       ├── user-validation.js
│   │       ├── account-setup.js
│   │       └── welcome-message.js
│   └── shared/
│       └── scripts/
│           ├── common-validators.js
│           ├── date-utilities.js
│           └── api-helpers.js
```

**Organization Guidelines:**

- Each workflow folder should contain its own `scripts` subfolder
- Shared utilities should be placed in a `shared/scripts` folder
- Name files descriptively based on their function
- Group related scripts by subdirectory when you have many files
- Use `.js` extension for standard JavaScript, `.jsw` for workflow-specific scripts

### 5.2. Security Considerations

**Environment Variables:**

- Always use `$env.get()` for sensitive data like API keys, passwords, or tokens
- Never hardcode sensitive information in your scripts
- Use descriptive environment variable names

```javascript
// ✅ Good - Using environment variables
const apiKey = $env.get('API_SECRET_KEY');
const dbPassword = $env.get('DATABASE_PASSWORD');

// ❌ Bad - Hardcoded sensitive data
const apiKey = 'sk-1234567890abcdef';
```

**Data Validation:**

- Always validate input data before processing
- Sanitize user input to prevent injection attacks
- Use type checking and bounds validation

```javascript
// ✅ Good - Input validation
const userInput = $memory.get('user_input', '');
if (typeof userInput !== 'string' || userInput.length > 1000) {
    $memory.set('validation_error', 'Invalid input format or length');
    // Use next_failed to handle validation error
}

const sanitizedInput = userInput.replace(/[<>]/g, '');
```

**Error Handling:**

- Always provide meaningful error messages
- Use try-catch blocks for potentially failing operations
- Log errors for debugging without exposing sensitive information

```javascript
try {
    const result = processComplexCalculation(data);
    $memory.setJson('calculation_result', { success: true, result }, 3600);
} catch (error) {
    $utils.logger.log('Calculation Error', { 
        error: error.message,
        userId: $user.get('id')
    });
    $memory.setJson('calculation_result', { 
        success: false, 
        error: 'Calculation failed. Please try again.' 
    }, 3600);
    // Use next_failed to handle calculation error
}
```

### 5.3. Performance Optimization

**Memory Management:**

- Clean up large objects after use
- Use `$memory.set()` strategically to avoid memory bloat
- Remove temporary variables when no longer needed

```javascript
// Process large dataset
const processedData = transformLargeDataset(rawData);
$memory.set('processed_results', processedData);

// Clean up temporary data
rawData = null;
intermediateResults = null;
```

**Efficient Data Processing:**

- Use Lodash utilities for complex data operations
- Avoid nested loops when possible
- Cache frequently accessed data

```javascript
// ✅ Efficient - Using Lodash
const activeUsers = $utils._.filter(users, { status: 'active' });
const usersByRegion = $utils._.groupBy(activeUsers, 'region');

// ❌ Inefficient - Manual loops
const activeUsers = [];
for (let i = 0; i < users.length; i++) {
    if (users[i].status === 'active') {
        activeUsers.push(users[i]);
    }
}
```

### 5.4. Maintainability

**Function Organization:**

- Break complex code into smaller, focused functions
- Use descriptive function and variable names
- Add comments for complex business logic

```javascript
// ✅ Well-organized code
function calculateCreditScore(transactions, accountInfo) {
    const paymentHistory = analyzePaymentHistory(transactions);
    const utilization = calculateUtilization(accountInfo);
    const accountAge = calculateAccountAge(accountInfo.openedDate);
    
    return computeFinalScore(paymentHistory, utilization, accountAge);
}

function analyzePaymentHistory(transactions) {
    // Focused function with single responsibility
    return $utils._.filter(transactions, t => !t.latePayment).length / transactions.length;
}
```

**Documentation:**

- Document expected input/output formats
- Explain complex algorithms or business rules
- Include examples of usage

```javascript
/**
 * Calculates user engagement score based on activity metrics
 * @param {Object} activityData - User activity data
 * @param {number} activityData.loginCount - Number of logins in period
 * @param {number} activityData.timeSpent - Total time spent in minutes
 * @param {Array} activityData.actions - List of user actions
 * @returns {Object} - Score object with value and breakdown
 */
function calculateEngagementScore(activityData) {
    // Implementation here
}
```

### 5.5. Testing and Debugging

**Use Logging Strategically:**

- Log important decision points and data transformations
- Include context for debugging
- Avoid logging sensitive information

```javascript
$utils.logger.log('User Validation', {
    userId: $user.get('id'),
    validationStep: 'email_format',
    isValid: emailValid,
    timestamp: $utils.dayjs().toISOString()
});
```

**Error Recovery:**

- Provide fallback values for missing data
- Graceful degradation when optional features fail
- Clear error messages for users

```javascript
const userPreferences = $memory.getJson('user_preferences', {
    theme: 'light',
    language: 'en',
    notifications: true
});

// Graceful fallback if API call fails
let locationData;
try {
    locationData = await getLocationFromAPI();
} catch (error) {
    locationData = { city: 'Unknown', country: 'Unknown' };
    $utils.logger.log('Location API Failed', { error: error.message });
}
```

## 6. Integration Patterns

### 6.1. Working with HTTP Blocks

Use code blocks to process and validate HTTP responses before using the data:

```hcl
// 1. Make API call
http "fetch_user_data" {
    method = "GET"
    url = "https://api.example.com/users/{{user_id}}"
    headers = {
        Authorization = "Bearer {{api_token}}"
    }
    next = "process_api_response"
    next_failed = "api_error_handler"
}

// 2. Process the response with code block
code "process_api_response" {
    runtime = "javascript"
    code = `
        const response = $context.getHttpResponse('fetch_user_data');
        
        // Validate response structure
        if (!response.data || !response.data.user) {
            $memory.setJson('api_error', { 
                success: false, 
                error: 'Invalid response format' 
            }, 3600);
            // Use next_failed to handle API error
        }
        
        const userData = response.data.user;
        
        // Transform and validate data
        const processedUser = {
            id: userData.id,
            name: userData.full_name || 'Unknown',
            email: userData.email_address,
            isActive: userData.status === 'active',
            lastLogin: userData.last_login_date ? 
                $utils.dayjs(userData.last_login_date) : null,
            preferences: userData.user_preferences || {}
        };
        
        // Store processed data
        $memory.setJson('current_user', processedUser, 3600);
    `
    next = "display_user_info"
    next_failed = "data_processing_error"
}
```

### 6.2. Working with Conditional Blocks

Prepare data and set flags for conditional logic:

```hcl
// 1. Process user data and set decision flags
code "prepare_user_routing" {
    runtime = "javascript"
    code = `
        const userProfile = $memory.getJson('user_profile');
        const accountInfo = $memory.getJson('account_info');
        
        // Business logic for routing decisions
        const isVIPCustomer = userProfile.accountType === 'premium' && 
                             accountInfo.monthlySpending > 10000;
        
        const needsVerification = !userProfile.emailVerified || 
                                 !userProfile.phoneVerified;
        
        const hasActiveIssues = accountInfo.pendingTickets > 0 || 
                               accountInfo.accountLocked;
        
        // Set routing flags
        $memory.set('is_vip_customer', isVIPCustomer);
        $memory.set('needs_verification', needsVerification);
        $memory.set('has_active_issues', hasActiveIssues);
    `
    next = "route_user_experience"
}

// 2. Use conditional block with prepared flags
conditional "route_user_experience" {
    conditions = [
        {
            id = "vip_priority"
            terms = [{
                operator = "equal"
                value1 = "{{$memory.is_vip_customer}}"
                value2 = true
            }]
            next = "vip_customer_flow"
        },
        {
            id = "verification_needed"
            terms = [{
                operator = "equal"
                value1 = "{{$memory.needs_verification}}"
                value2 = true
            }]
            next = "verification_flow"
        },
        {
            id = "has_issues"
            terms = [{
                operator = "equal"
                value1 = "{{$memory.has_active_issues}}"
                value2 = true
            }]
            next = "issue_resolution_flow"
        }
    ]
    next = "standard_customer_flow"
}
```

### 6.3. Working with AI Blocks

Prepare context and process AI responses:

```hcl
// 1. Prepare context for AI interaction
code "prepare_ai_context" {
    runtime = "javascript"
    code = `
        const TTL_1H = 3600;
        const userHistory = $memory.getJson('conversation_history', []);
        const userProfile = $memory.getJson('user_profile', {});
        const currentIssue = $memory.getJson('current_issue', {});
        
        // Build context for AI
        const aiContext = {
            user: {
                name: userProfile.name,
                accountType: userProfile.accountType,
                preferredLanguage: userProfile.language || 'en'
            },
            conversation: {
                messageCount: userHistory.length,
                lastTopics: userHistory.slice(-3).map(msg => msg.topic),
                sentiment: calculateSentiment(userHistory)
            },
            issue: {
                category: currentIssue.category,
                priority: currentIssue.priority,
                description: currentIssue.description
            }
        };
        
        function calculateSentiment(history) {
            // Simple sentiment analysis
            const negativeWords = ['angry', 'frustrated', 'upset', 'bad', 'terrible'];
            const recentMessages = history.slice(-5).join(' ').toLowerCase();
            
            return negativeWords.some(word => recentMessages.includes(word)) 
                ? 'negative' : 'neutral';
        }
        
        $memory.setJson('ai_context', aiContext, TTL_1H);
    `
    next = "ai_customer_support"
}

// 2. AI interaction with prepared context
ai "ai_customer_support" {
    model = "gpt-4o"
    prompt = `You are a customer support agent helping {{$memory.ai_context.user.name}}.
    
    User Details:
    - Account Type: {{$memory.ai_context.user.accountType}}
    - Language: {{$memory.ai_context.user.preferredLanguage}}
    - Current Issue: {{$memory.ai_context.issue.description}}
    - Issue Priority: {{$memory.ai_context.issue.priority}}
    
    Recent conversation sentiment: {{$memory.ai_context.conversation.sentiment}}
    
    Provide helpful, personalized assistance based on their account type and issue priority.`
    variable = "ai_response"
    next = "process_ai_response"
}

// 3. Process AI response
code "process_ai_response" {
    runtime = "javascript"
    code = `
        const TTL_1H = 3600;
        const aiResponse = $memory.get('ai_response', ''); // primitive
        const aiContext = $memory.getJson('ai_context', {});
        
        // Log interaction for analytics
        $utils.logger.log('AI Interaction', {
            userId: $user.get('id'),
            issueCategory: aiContext.issue.category,
            responseLength: aiResponse.length,
            sentiment: aiContext.conversation.sentiment,
            timestamp: $utils.dayjs().toISOString()
        });
        
        // Determine if escalation is needed
        const escalationKeywords = ['escalate', 'manager', 'supervisor', 'human agent'];
        const needsEscalation = escalationKeywords.some(keyword => 
            aiResponse.toLowerCase().includes(keyword)
        );
        
        $memory.set('needs_escalation', needsEscalation);
        $memory.setJson('processed_ai_response', {
            content: aiResponse,
            needsEscalation: needsEscalation,
            timestamp: $utils.dayjs().toISOString()
        }, TTL_1H);
    `
    next = "check_escalation_needed"
}
```

### 6.4. Working with Input Blocks

Validate and process user input:

```hcl
// 1. Collect user input
input "collect_phone_number" {
    prompt = "Please enter your phone number:"
    variable = "raw_phone_input"
    next = "validate_phone_number"
    next_expired = "phone_input_timeout"
    next_exit = "user_cancelled_phone"
}

// 2. Validate and format input
code "validate_phone_number" {
    runtime = "javascript"
    code = `
        const rawPhone = $memory.get('raw_phone_input', '');
        
        // Clean and validate phone number
        const cleanPhone = rawPhone.replace(/[^\d+]/g, '');
        
        // Validation patterns for different formats
        const patterns = {
            us: /^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$/,
            international: /^\+[1-9]\d{1,14}$/,
            general: /^\+?[\d]{7,15}$/
        };
        
        let isValid = false;
        let format = 'invalid';
        let formattedPhone = cleanPhone;
        
        if (patterns.us.test(cleanPhone)) {
            isValid = true;
            format = 'us';
            // Format as (XXX) XXX-XXXX
            const match = cleanPhone.match(/(\d{3})(\d{3})(\d{4})$/);
            if (match) {
                formattedPhone = \\`(\\${match[1]}) \\${match[2]}-\\${match[3]}\\`;
            }
        } else if (patterns.international.test(cleanPhone)) {
            isValid = true;
            format = 'international';
            formattedPhone = cleanPhone;
        } else if (patterns.general.test(cleanPhone)) {
            isValid = true;
            format = 'general';
            formattedPhone = cleanPhone;
        }
        
        const result = {
            raw: rawPhone,
            cleaned: cleanPhone,
            formatted: formattedPhone,
            isValid: isValid,
            format: format
        };
        
        $memory.setJson('phone_validation_result', result, TTL_1H);
        
        if (isValid) {
            $memory.set('user_phone', formattedPhone);
        }
    `
    next = "check_phone_validation"
}

// 3. Handle validation result
conditional "check_phone_validation" {
    conditions = [
        {
            id = "phone_valid"
            terms = [{
                operator = "equal"
                value1 = "{{$memory.phone_validation_result.isValid}}"
                value2 = true
            }]
            next = "phone_accepted"
        }
    ]
    next = "phone_invalid"
}
```

### 6.5. Dynamic Message Generation

Generate dynamic content for message blocks:

```hcl
// 1. Generate personalized content
code "generate_message_content" {
    runtime = "javascript"
    code = `
        const userProfile = $memory.getJson('user_profile');
        const accountInfo = $memory.getJson('account_info');
        const currentTime = $utils.dayjs();
        
        // Generate greeting based on time and user preference
        const hour = currentTime.hour();
        let greeting;
        
        if (userProfile.preferredLanguage === 'es') {
            if (hour < 12) greeting = 'Buenos días';
            else if (hour < 18) greeting = 'Buenas tardes';
            else greeting = 'Buenas noches';
        } else {
            if (hour < 12) greeting = 'Good morning';
            else if (hour < 18) greeting = 'Good afternoon';
            else greeting = 'Good evening';
        }
        
        // Generate personalized message
        const messageContent = {
            greeting: \\`\\${greeting}, \\${userProfile.firstName}!\\`,
            balanceInfo: \\`Your current balance is $\\${accountInfo.balance.toLocaleString()}\\`,
            lastTransaction: accountInfo.lastTransaction ? 
                \\`Last transaction: \\${accountInfo.lastTransaction.description} - $\\${accountInfo.lastTransaction.amount}\\` :
                'No recent transactions',
            tips: generatePersonalizedTips(userProfile, accountInfo)
        };
        
        function generatePersonalizedTips(profile, account) {
            const tips = [];
            
            if (account.balance < 1000) {
                tips.push("💡 Consider setting up automatic savings to build your emergency fund");
            }
            
            if (profile.accountType === 'basic' && account.monthlyTransactions > 20) {
                tips.push("⭐ You're an active user! Upgrade to Premium for unlimited transactions");
            }
            
            return tips;
        }
        
        $memory.setJson('personalized_message', messageContent, 500);
    `
    next = "send_personalized_message"
}

// 2. Send dynamic message
message "send_personalized_message" {
    type = text
    text = `{{$memory.personalized_message.greeting}}

{{$memory.personalized_message.balanceInfo}}
{{$memory.personalized_message.lastTransaction}}

{{#each $memory.personalized_message.tips}}
{{this}}
{{/each}}`
    next = "show_main_menu"
}
```

These integration patterns demonstrate how code blocks serve as the "glue" that connects different workflow components, enabling complex business logic, data transformation, and dynamic content generation within your workflows.
