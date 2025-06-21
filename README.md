# E-commerce Admin Dashboard: An AOP Showcase

This project is a minimalist E-commerce Admin Dashboard built with Flask, designed to be a practical and theoretical showcase of Aspect-Oriented Programming (AOP) in Python. It demonstrates how to use decorators to implement common cross-cutting concerns in a clean and modular way.

## Tech Stack
*   **Backend**: Flask
*   **Frontend**: Jinja2 (with a "micro-frontend" approach using template fragments)
*   **Database**: SQLite
*   **Testing**: Pytest

---

## AOP Concepts Demonstrated

This dashboard implements the following AOP concepts exclusively through decorators:

1.  **Security (`@secure`)**: Role-based access control for specific routes.
2.  **Caching (`@cache`)**: Caching view results in-memory to improve performance.
3.  **Metrics (`@metrics`)**: Measuring the execution time of a request.
4.  **Auditing (`@audit`)**: Logging user actions for security and traceability.
5.  **Feature Flags (`@feature_flag`)**: Toggling access to features at runtime without deploying new code.

---

## Architecture

The application follows a modular structure using Flask Blueprints. Each feature (Products, Orders, etc.) is a separate blueprint. The AOP decorators are applied to the view functions within these blueprints.

```
┌────────────────────────────────────────────┐
│                  Flask App                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Auth BP  │  │Products BP │  │ Orders BP  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│     │             │              │       │
│    @secure       @cache        @audit   │
│                  @metrics               │
│                                          │
│  ┌──────────────┐  ┌───────────────┐     │
│  │TransactionsBP│  │ Promotions BP │     │
│  └──────────────┘  └───────────────┘     │
│    @cache            @feature_flag      │
│    @metrics                             │
└────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites
*   Python 3.6+
*   `venv` or your preferred virtual environment tool
*   `uv` (or `pip`) for package installation

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd project-pc3
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

3.  **Initialize the database:**
    This command will create the `project.sqlite` file and populate it with seed data.
    ```bash
    flask --app app init-db
    ```
    You should see an "Initialized the database." message.

4.  **Run the application:**
    ```bash
    flask --app run
    ```
    The application will be running at `http://127.0.0.1:5000`.

### Running Tests
To run the unit tests for the decorators:
```bash
pytest
```

---

## How to Use & AOP in Action

1.  **Login**:
    Navigate to `http://127.0.0.1:5000` and log in with the credentials:
    *   **Username**: `admin`
    *   **Password**: `admin`

2.  **Observe the Decorators**:
    As you navigate the dashboard, check the console where you ran `flask run`. You will see output from the AOP decorators.

    *   **`@secure`**: Try accessing a protected route like `/auth/admin_only`. You'll see the security check in the log.
        ```
        SECURITY: Access granted to user 'admin' with role 'admin'.
        ```

    *   **`@cache` & `@metrics`**: Load the "Products" page. The first time, it will be a cache "miss". Reload the page, and you'll see a cache "hit" with a faster execution time.
        ```
        # First load
        METRICS for 'list_products':
          - Execution Time: 0.0025s
        CACHE: Miss for key 'list_products:{}'. Caching result.

        # Second load
        METRICS for 'list_products':
          - Execution Time: 0.0001s
        CACHE: Hit for key 'list_products:{}'.
        ```

    *   **`@audit`**: Click on an "Order Details" link. The console will log the action.
        ```
        AUDIT: User 'admin' performed action 'view_order' with args {'id': 1}.
        ```

    *   **`@feature_flag`**: Navigate to the "Promotions" page. By default, the `promo_editor` feature is disabled.
        ```
        FEATURE_FLAG: 'promo_editor' is OFF. Access denied.
        ```
        You can enable it by changing the `is_active` flag in the `feature_flag` table in the database.
