# Authentication & Role-Based Access Control (RBAC)

The AI Circular Economy Marketplace implements a secure, stateless authentication and authorization framework powered by JWT (JSON Web Tokens) and bcrypt password hashing.

---

## User Roles & Capabilities

| Role | Permitted Actions | Restricted Actions |
|---|---|---|
| **Seller** | List materials, upload images for AI analysis, set asking prices, view/counter/accept buyer offers, coordinate dispatches, schedule pickups, chat on confirmed transactions. | Cannot create buyer sourcing requirements or submit offers on marketplace listings. |
| **Buyer** | Browse listings, filter by distance, register sourcing requirements, submit purchase offers, counter seller proposals, confirm receipts, chat on confirmed orders. | Cannot create seller inventory or list raw materials. |
| **Admin** | Manage users, oversee all listings and transactions, inspect ML performance metrics, update global sustainability conversion factors, view system-wide analytics. | Platform-wide administrative authority. |

---

## Authentication Endpoints

### 1. User Registration
`POST /api/auth/register`

**Payload:**
```json
{
  "name": "Coimbatore Metals Pvt Ltd",
  "email": "seller@coimbatoremetals.com",
  "password": "SecurePassword123!",
  "role": "seller",
  "organization": "Coimbatore Metals",
  "business_type": "Scrap Processor",
  "materials_interested": "Aluminum, Copper",
  "city": "Coimbatore",
  "state": "Tamil Nadu",
  "latitude": 11.0168,
  "longitude": 76.9558
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-v4",
    "name": "Coimbatore Metals Pvt Ltd",
    "email": "seller@coimbatoremetals.com",
    "role": "seller",
    "organization": "Coimbatore Metals",
    "business_type": "Scrap Processor",
    "city": "Coimbatore",
    "state": "Tamil Nadu"
  }
}
```

### 2. User Login
`POST /api/auth/login`

**Payload:**
```json
{
  "email": "seller@coimbatoremetals.com",
  "password": "SecurePassword123!"
}
```

### 3. Current User Context
`GET /api/auth/me`

Requires Header:
`Authorization: Bearer <access_token>`

---

## Security Implementation

- **Password Hashing**: Cryptographic password hashing using `passlib[bcrypt]` with dynamic work factor. Plaintext passwords are never logged or stored.
- **Token Verification**: Handled via `backend/app/core/security.py` using `python-jose` with configurable secret keys and token expiration times (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Endpoint Protection**: Implemented through FastAPI dependency injection:
  ```python
  @router.post("/api/offers/{id}/accept")
  def accept_offer(
      id: str,
      db: Session = Depends(get_db),
      current_user: User = Depends(require_role(["seller", "buyer"]))
  ):
      ...
  ```
