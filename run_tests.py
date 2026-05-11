import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import User
from sqlalchemy import select
from app.middleware.rbac import create_access_token
import json
import uuid

async def get_user_token(email: str):
    async with AsyncSessionLocal() as db:
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalar_one_or_none()
        if not user:
            print(f"User {email} not found!")
            return None, None
        token = create_access_token(str(user.id), user.role.value, user.email)
        
        manager_email = None
        if user.manager_id:
            manager = await db.get(User, user.manager_id)
            if manager:
                manager_email = manager.email
                
        return token, manager_email

async def run_query(client, token, message, session_id):
    print(f"\n[User]: {message}")
    response = await client.post(
        "http://127.0.0.1:8000/api/v1/chat",
        json={"message": message, "session_id": session_id},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0
    )
    if response.status_code == 200:
        data = response.json()
        print(f"[Aura]: {data.get('response')}")
        return data
    else:
        print(f"[Error]: {response.status_code} - {response.text}")
        return None

async def main():
    email = "emp.2@novigosolutions.com"
    token, manager_email = await get_user_token(email)
    if not token:
        return
    
    print(f"Logged in as {email}")
    print(f"Manager is {manager_email}")
    
    manager_token, _ = await get_user_token(manager_email) if manager_email else (None, None)
    
    session_id = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        # Test 1: Earned Leave
        await run_query(client, token, "I want 2 days of earned leave starting tomorrow. I will be going on a vacation", session_id)
        
        # Test 2: Sick Leave on May 16
        await run_query(client, token, "I want to apply for sick leave on 16th May.", session_id)
        
        # Test 3: Paternity Leave starting 25th May
        await run_query(client, token, "I want to take paternity leave for 2 days starting 25th May", session_id)
        
        # Test 4: Backdated Leave
        await run_query(client, token, "I want to take casual leave for 1 day on 1st May 2026.", session_id)
        
        # Test 5: View Leave History to test cancel_leave
        res = await run_query(client, token, "Show me my leave history", session_id)
        
        # Test 6: Cancel leave
        await run_query(client, token, "Cancel my sick leave request.", session_id)
        
        # Test 7: HR Policies
        await run_query(client, token, "What is the policy for work from home?", session_id)
        
        # Test 8: Manager approves leave
        if manager_token:
            print("\n[Switching to Manager]")
            manager_session_id = str(uuid.uuid4())
            await run_query(client, manager_token, "Are there any pending leave requests for my team?", manager_session_id)

if __name__ == "__main__":
    asyncio.run(main())
