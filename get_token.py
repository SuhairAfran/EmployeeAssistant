from app.middleware.rbac import create_access_token

# Mint a 8-hour token using Bob's exact details from the database
bob_token = create_access_token(
    user_id="33333333-3333-3333-3333-333333333333",
    role="employee",
    email="bob.employee@company.com"
)

print("\n=== BOB'S JWT TOKEN ===")
print(bob_token)
print("=======================\n")