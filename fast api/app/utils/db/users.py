from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ...models import User
from ...schemas import users as user_schemas
from ..auth.hashing import Hash


def get_user_by_email(email: EmailStr, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


def get_user_or_404(email: EmailStr, db: Session) -> User:
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def create_new_user(request: user_schemas.UserCreate, db: Session) -> User:
    existing_user = get_user_by_email(request.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
        )

    hashed_password = Hash.hash_password(password=request.password)

    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(user: User, user_update: user_schemas.UserUpdate, db: Session) -> User:
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(user: User, db: Session) -> None:
    db.delete(user)
    db.commit()
