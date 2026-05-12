import asyncio
from app.databases import async_session
from app.models.auth import User
from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def create_test_user():
    try:
        async with async_session() as session:
            # Check if user exists
            stmt = select(User).where(User.email == 'test@example.com')
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ User already exists: test@example.com")
                return
            
            # Create new user
            user = User(
                email='test@example.com',
                hashed_password=pwd_context.hash('TestPass123'),
                full_name='Test User',
                is_active=True
            )
            session.add(user)
            await session.commit()
            print("✅ Test user created successfully!")
            print("   Email: test@example.com")
            print("   Password: TestPass123")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(create_test_user())
