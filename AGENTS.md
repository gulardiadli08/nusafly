# AGENTS.md — Flight Ticket Booking Website

> **Project type:** MVP / learning project  
> **Team:** 2 people — Backend (Python) and Frontend  
> **Default language:** Indonesian for user-facing UI and project discussion; English for code identifiers and API fields  
> **Status:** Initial specification. If the repository already has an established implementation, inspect it before changing architecture.

## 1. Purpose and product scope

Build a web application that lets users search for flights, review flight details, enter passenger information, create bookings, simulate or integrate a payment flow, and view booking status/history.

The first version uses **seeded/demo flight data** unless the team explicitly configures a legitimate flight-data provider. Do not imply that demo flights are real, bookable airline inventory, or live fares.

### MVP features

1. Public home page and flight search.
2. Search by origin, destination, departure date, passenger count, and cabin class if supported.
3. Search results with airline, flight number, departure/arrival airports and times, duration, stops, fare, and remaining demo seats where available.
4. Flight detail and fare summary.
5. User registration, login, logout, and profile.
6. Passenger details form and booking creation.
7. Booking reference / booking code and booking detail page.
8. Booking list/history for the authenticated user.
9. Booking cancellation according to the project's simple policy.
10. Payment simulation with explicit `PENDING`, `PAID`, `FAILED`, and `REFUNDED` or `CANCELLED` states as appropriate.
11. Basic admin management of demo airports, airlines, flights, fares, and bookings through Django Admin.
12. Responsive and accessible interface, including loading, empty, validation, and error states.

### Out of scope for the initial MVP

- Direct airline reservation-system (GDS) integration.
- Real ticket issuance or claims that a booking is confirmed with an airline.
- Storing card numbers, CVV, bank credentials, or payment secrets.
- Loyalty programs, complex refunds, multi-city journeys, seat maps, and promotional engines unless agreed later.
- Production launch with real payments before security, legal, provider, and operational review.

## 2. Team responsibilities

### Backend developer (project owner)

Owns:
- Django project setup and configuration.
- Database schema, migrations, seed/demo data, and Django Admin.
- REST API design and implementation.
- Authentication, authorization, validation, business rules, and error responses.
- Search/filter logic, price calculation, booking lifecycle, inventory protection, and payment simulation/provider integration.
- API tests, security checks, API documentation, environment configuration, and backend deployment.

Must provide the frontend developer with:
- API endpoint list and examples.
- Request/response JSON examples.
- Authentication method and expected error format.
- Enum values, required fields, validation rules, and status transitions.
- Seed accounts/data for local testing, with no production secrets.

### Frontend developer

Owns:
- Page layouts, responsive styling, reusable components, and navigation.
- Search form, search results, flight detail, passenger form, checkout, booking confirmation, login/register, profile, and booking history UI.
- API client layer and integration with backend endpoints.
- Form validation for usability (backend remains authoritative).
- Loading, empty, success, and error states.
- Accessibility, responsive behavior, and frontend tests where practical.

Must not:
- Connect directly to the database.
- Treat client-side price, role, booking status, or payment status as authoritative.
- place secrets, API keys, or privileged business logic in browser code.
- invent endpoint fields or statuses; coordinate contract changes with backend.

### Shared responsibilities

- Agree on API contracts before parallel implementation.
- Use Git branches and pull requests (or reviewed merges).
- Review each other's changes and test the integrated application.
- Keep README, setup instructions, and known limitations current.
- Discuss breaking API changes before implementing them.

## 3. Recommended stack

### Backend
- Python: use a currently supported Python 3 version compatible with the selected Django release.
- Django.
- Django REST Framework (DRF).
- PostgreSQL for shared development and deployment; SQLite may be used for a quick local bootstrap if configured intentionally.
- `django-environ` or equivalent for environment variables.
- `django-filter` where useful.
- `drf-spectacular` or equivalent for OpenAPI documentation.
- `pytest` + `pytest-django` or Django's built-in test framework.
- `ruff` for linting/formatting, if agreed by the team.

### Frontend
Choose one approach and document it in the README:
- **Simple option:** Django-independent HTML/CSS/JavaScript with Bootstrap or Tailwind CSS.
- **Separate app option:** React + TypeScript + Vite.

Do not introduce React, a CSS framework, state-management library, or other major dependency without team agreement. The frontend calls the REST API and does not duplicate backend business rules.

### Tooling
- Git and a shared remote repository.
- `.env` for local secrets/configuration; `.env.example` for documented variable names and safe example values.
- Docker Compose is optional, but useful if both developers need consistent PostgreSQL setup.
- CI should run backend tests and lint checks when practical.

Pin compatible dependency versions in the project's dependency files. Do not blindly upgrade major versions.

## 4. Suggested repository structure

Adapt this structure to the agreed frontend approach. Do not move or rename existing files without inspecting the repository and explaining the reason.

```text
flight-booking/
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/
│   │   ├── airports/
│   │   ├── airlines/
│   │   ├── flights/
│   │   ├── bookings/
│   │   └── payments/
│   ├── tests/
│   └── requirements.txt
├── frontend/                 # if frontend is a separate application
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/
│   ├── API.md
│   ├── API_CONTRACTS.md
│   └── decisions/
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

Use Django apps only where they represent clear domain boundaries. Avoid creating many tiny apps without a practical reason.

## 5. Domain model guidance

Names below are suggestions. Inspect existing models and avoid duplicating equivalent entities.

### Airport
- `id`
- `iata_code` (unique, 3 uppercase letters where applicable)
- `name`
- `city`
- `country`
- `timezone` (IANA timezone identifier)

### Airline
- `id`
- `iata_code` (unique where applicable)
- `name`
- `logo_url` (optional; validate trusted sources if used)

### Flight
For an MVP, a `Flight` record can represent a scheduled flight instance, not merely a reusable route.
- `id`
- `airline` (foreign key)
- `flight_number`
- `origin_airport` (foreign key to Airport)
- `destination_airport` (foreign key to Airport)
- `departure_at` and `arrival_at` (timezone-aware datetimes)
- `base_price` / fare amount using `DecimalField`, never binary float
- `currency` (for example, `IDR`)
- `available_seats` or inventory fields appropriate to the selected model
- `status` (for example, `SCHEDULED`, `CANCELLED`)
- timestamps

Validation:
- Origin and destination must differ.
- Arrival must be later than departure, accounting for timezone-aware datetimes.
- Search should only return eligible scheduled flights.
- Do not assume that a city's local time is UTC. Store aware datetimes and display them in the airport's timezone.

### Booking
- `id`
- `booking_code` (unique, hard to guess, generated server-side)
- `user` (foreign key)
- `flight` (foreign key for the MVP's single-flight booking)
- `status` (for example, `PENDING_PAYMENT`, `CONFIRMED`, `CANCELLED`, `EXPIRED`)
- `passenger_count`
- `subtotal`, `taxes`, `fees`, `total_amount` using decimal money fields
- `currency`
- `created_at`, `updated_at`, optional `expires_at`

Persist a **price snapshot** on the booking. Do not calculate the displayed historical total solely from a fare that may later change.

### Passenger
- `id`
- `booking` (foreign key)
- `full_name`
- `date_of_birth` only if needed
- `document_type` and `document_number` only if genuinely required for the project's use case
- other minimum necessary passenger fields

Collect only data needed for the agreed demo and provider rules. Avoid storing sensitive identity data without a clear need and appropriate safeguards.

### Payment
- `id`
- `booking` (foreign key; define whether one or multiple attempts are allowed)
- `provider_reference` (nullable)
- `amount` and `currency`
- `status` (`PENDING`, `SUCCEEDED`, `FAILED`, `REFUNDED` as appropriate)
- `created_at`, `updated_at`

Never store raw card details, CVV, bank passwords, or payment credentials.

### User
Use Django's authentication system and a custom user model from the beginning if custom identity fields are required. Do not implement password storage manually. If a custom user model is planned, configure it before the first migration.

## 6. API conventions

- Prefix API routes with `/api/v1/`.
- Use JSON request/response bodies unless an endpoint explicitly requires another format.
- Use plural resource names, consistent naming, and appropriate HTTP methods/status codes.
- Document endpoints in `docs/API.md` or OpenAPI.
- Return predictable errors, for example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Periksa kembali data yang dikirim.",
    "details": {
      "departure_date": ["Tanggal keberangkatan wajib diisi."]
    }
  }
}
```

Use a consistent error schema across endpoints; if DRF defaults are retained, document them and keep frontend handling consistent.

### Initial endpoint proposal

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/api/v1/airports/` | List/search airports | Public |
| GET | `/api/v1/airlines/` | List airlines | Public |
| GET | `/api/v1/flights/` | Search flights with query parameters | Public |
| GET | `/api/v1/flights/{id}/` | Flight details | Public |
| POST | `/api/v1/auth/register/` | Register account | Public |
| POST | `/api/v1/auth/login/` | Login | Public |
| POST | `/api/v1/auth/logout/` | Logout where supported | Authenticated |
| GET | `/api/v1/me/` | Current user's profile | Authenticated |
| POST | `/api/v1/bookings/` | Create booking | Authenticated |
| GET | `/api/v1/bookings/` | List current user's bookings | Authenticated |
| GET | `/api/v1/bookings/{id}/` | Get an owned booking | Authenticated |
| POST | `/api/v1/bookings/{id}/cancel/` | Request cancellation | Authenticated |
| POST | `/api/v1/bookings/{id}/payment/` | Start demo/provider payment | Authenticated |
| GET | `/api/v1/bookings/{id}/payment-status/` | Retrieve payment state | Authenticated |

These are proposed contracts, not claims that endpoints already exist. Agree on exact fields and authentication behavior before frontend integration. A public booking lookup, if added, must require a sufficiently strong booking code and additional verification rather than exposing records by sequential IDs.

### Flight search parameters

Example:
`GET /api/v1/flights/?origin=CGK&destination=DPS&departure_date=2026-12-20&passengers=1`

Define and validate:
- `origin`: airport IATA code.
- `destination`: airport IATA code.
- `departure_date`: ISO date (`YYYY-MM-DD`) in the origin airport's local calendar.
- `passengers`: positive integer within a documented limit.
- optional `cabin_class`, `sort`, and pagination only if implemented.

Reject invalid dates, unsupported filters, origin equal to destination, and passenger counts outside the documented range. Never trust a client-supplied price.

## 7. Booking and inventory rules

1. Re-fetch the flight and current fare on the server when a booking is created.
2. Calculate all amounts on the backend using `Decimal`; do not accept a final total from the browser.
3. Validate that the flight is eligible and has sufficient inventory.
4. Use a database transaction and appropriate row locking/atomic updates to prevent two users from taking the same final seat.
5. Define whether inventory is reserved at booking creation or after payment initiation; document the chosen rule.
6. If using a pending-payment hold, give it a documented expiration time and release held inventory when it expires or is cancelled.
7. Make booking creation and payment callbacks idempotent: retries must not create duplicate bookings or mark a payment twice.
8. A booking becomes confirmed only after the backend verifies successful payment (or after an explicit demo-payment success action in development).
9. Validate that the authenticated user owns a booking before reading, cancelling, or paying for it.
10. Make cancellation and payment status transitions explicit and tested.
11. Use server-side time and timezone-aware values for expiration checks.
12. Record meaningful status changes for troubleshooting, without logging secrets or sensitive passenger data.

For the demo payment flow, display clear wording that it is simulated. Do not claim that money was actually charged.

## 8. Security requirements

- Keep `DEBUG=False` in production.
- Load `SECRET_KEY`, database credentials, payment keys, and other secrets from environment variables.
- Never commit `.env`, real credentials, access tokens, or private keys.
- Configure `ALLOWED_HOSTS`, CORS, CSRF, HTTPS, cookies, and trusted origins correctly for the deployment.
- Use Django password hashing and the framework's authentication protections.
- Apply authentication and object-level authorization to private endpoints.
- Prevent insecure direct object reference (IDOR): users must not access another user's bookings by changing an ID.
- Validate and normalize all user input on the server.
- Use ORM queries; avoid constructing raw SQL from user input.
- Add rate limiting/throttling to sensitive endpoints where appropriate, especially login and registration.
- Avoid leaking stack traces, internal errors, secrets, or private data in API responses.
- Do not log passwords, tokens, payment secrets, full identity document numbers, or card data.
- Use HTTPS in deployed environments.
- Use CSRF protections if using cookie/session authentication. If using token authentication, document storage and refresh/revocation behavior and never place long-lived secrets in unsafe browser storage.
- Configure upload validation if file uploads are introduced; do not add uploads unless needed.
- Keep dependencies updated with deliberate, tested changes.

## 9. Frontend integration requirements

- Keep the API base URL in environment/configuration, not duplicated throughout components.
- Centralize HTTP requests in an API client module.
- Handle unauthorized, forbidden, validation, network, and server errors consistently.
- Do not hardcode demo results in production UI; use the backend's seed data or clearly isolated mock fixtures.
- Never rely on frontend-only validation for security or business rules.
- Format currency consistently using Indonesian Rupiah for IDR amounts.
- Display departure and arrival times with airport timezone context where appropriate.
- Provide accessible labels, keyboard navigation, focus indicators, and sufficient contrast.
- Include loading, empty, retry, and error states.
- Prevent duplicate submit actions while a request is in progress.
- Do not expose internal exception details to users.
- Avoid storing sensitive passenger data in local storage or browser logs.

## 10. Git and collaboration workflow

Suggested branches:
- `main`: stable, integrated code.
- `backend/<short-description>`: backend work.
- `frontend/<short-description>`: frontend work.
- `feature/<short-description>`: cross-cutting feature, only when coordinated.

Workflow:
1. Create a task with a clear acceptance criterion.
2. Agree on API contract/model changes before parallel implementation.
3. Create a focused branch.
4. Make small, logical commits with clear messages.
5. Run tests and lint checks before merging.
6. Open a pull request or ask the other developer for review.
7. Resolve API conflicts explicitly; do not silently rename fields or statuses.
8. Update docs and `.env.example` when configuration or contracts change.
9. Merge only after the integrated path has been tested.

Commit examples:
- `feat(api): add flight search endpoint`
- `feat(ui): build flight search results`
- `fix(bookings): prevent duplicate seat allocation`
- `test(api): cover booking ownership`
- `docs: document authentication contract`

Do not commit generated caches, virtual environments, local databases containing personal data, build output, `.env`, or secrets.

## 11. Testing requirements

### Backend tests
- Flight search filters and invalid parameters.
- Flight detail returns the expected schema.
- Registration/login and permission behavior.
- Users cannot access another user's booking.
- Price is calculated from server-side data.
- Invalid passenger data is rejected.
- Booking fails if seats are insufficient.
- Concurrent booking cannot oversell inventory.
- Duplicate requests/payment callbacks are idempotent.
- Invalid status transitions are rejected.
- Cancellation releases inventory only according to the documented policy.
- Timezone/date boundary cases.
- API error response format remains consistent.

### Frontend / integration tests
- Search form submits expected query parameters.
- Results, empty state, and API errors render correctly.
- Login state and protected pages work.
- Passenger form displays validation feedback.
- Checkout cannot silently use a client-edited total.
- Booking confirmation and history use real API responses.
- Responsive layout works at mobile and desktop widths.

### Before declaring a feature done
- Tests pass.
- Permissions and validation are checked.
- API contract documentation is updated.
- Frontend and backend are tested together for the changed flow.
- No secrets or unnecessary personal data are introduced.

## 12. Local development and environment

Create a `.env.example` containing variable names and safe placeholders, such as:

```dotenv
DJANGO_SECRET_KEY=replace-for-local-development
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/flight_booking
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Adapt names to actual settings and selected frontend setup. `.env.example` must not contain real secrets.

Document exact setup commands in README. A typical backend workflow is:

```bash
python -m venv .venv
# Activate the virtual environment for your operating system
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Add a documented seed-data command or fixture so both developers can test with the same airports, airlines, and demo flights. Seed data must be safe, repeatable, and clearly marked as demo data.

## 13. Definition of done

A task is done only when:
- Its acceptance criteria are met.
- Relevant automated tests pass.
- Validation, permission checks, and error cases are handled.
- API contracts and developer documentation are updated.
- No secrets or unnecessary personal data are committed.
- The change works with the other half of the application.
- Known limitations are documented.

## 14. Instructions for AI coding agents

Before writing or changing code:
1. Inspect the repository, existing README, dependencies, settings, models, migrations, and tests.
2. Identify the current architecture and preserve working conventions.
3. State the intended changes briefly and identify affected files.
4. Check whether the task changes an API contract, database schema, authentication, or booking/payment behavior.
5. If a requirement is ambiguous and affects security, money, inventory, or data integrity, ask for clarification rather than guessing.

While implementing:
- Make the smallest coherent change that solves the task.
- Follow existing naming and formatting conventions.
- Keep views/controllers thin; place business rules in appropriate services/domain functions where useful.
- Use serializers/forms for input validation and ORM constraints for data integrity.
- Add migrations when models change; never silently edit an already-applied migration to alter shared history.
- Add tests for new behavior and regressions.
- Do not disable tests, authorization, CSRF, or validation merely to make a test pass.
- Do not add dependencies or refactor unrelated code without a clear reason.
- Never invent successful payment, airline availability, or booking confirmation.
- Never put secrets in source code, logs, fixtures, or responses.
- Do not run destructive commands or drop/clear shared data without explicit approval.

After implementing:
1. Summarize what changed and why.
2. List migrations and configuration changes.
3. Report commands/tests actually run and their results; do not claim tests passed if they were not run.
4. Mention API contract changes for the other developer.
5. List remaining risks, assumptions, or follow-up work.

## 15. Suggested implementation milestones

### Milestone 1 — Foundation
- Agree on stack and repository structure.
- Create Django project and frontend shell.
- Configure environment variables, database, Git, and README.
- Define API error conventions and authentication approach.

### Milestone 2 — Flight catalogue
- Create Airport, Airline, and Flight models.
- Add demo fixtures/seed command and Django Admin.
- Implement and test airport and flight search APIs.
- Build frontend search and results pages against the agreed contract.

### Milestone 3 — Accounts
- Implement registration, login/logout, profile, and permissions.
- Connect frontend forms and protected pages.
- Test unauthorized and cross-user access.

### Milestone 4 — Booking
- Add booking and passenger models.
- Implement server-side price calculation and inventory-safe booking.
- Build passenger entry, review, and confirmation screens.
- Test insufficient seats, duplicate submissions, and booking ownership.

### Milestone 5 — Payment simulation
- Implement payment state transitions and an explicit demo payment flow.
- Connect checkout and payment result UI.
- Test idempotency, failure, cancellation, and expiration rules.

### Milestone 6 — Integration and release
- Run full end-to-end flows and responsive checks.
- Review security settings, seed data, and error handling.
- Complete README and API docs.
- Deploy only to a suitable environment after configuration and security review.

## 16. Decisions to record before implementation

Record agreed answers in README or `docs/decisions/`:
- Is the frontend plain HTML/CSS/JavaScript or React + TypeScript?
- Is authentication session/cookie-based or token-based?
- Is PostgreSQL used from day one?
- Are bookings single-flight only for MVP?
- How is inventory held during payment, and when does the hold expire?
- Is payment simulation sufficient, or is a legitimate payment provider planned?
- Which timezone and currency conventions are used?
- What are the cancellation rules?
- What is the target deployment environment?
- Which API schema fields and status values are finalized?

**Priority rule:** security, data integrity, and an explicitly agreed API contract take precedence over convenience or assumptions made by an AI coding agent.
