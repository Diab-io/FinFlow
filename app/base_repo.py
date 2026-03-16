from typing import Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        return self.db.get(self.model, id)
    
    def list(self) -> list[ModelType]:
        stmt = select(self.model)
        return self.db.execute(stmt).scalars().all()
    
    def create(self, data: dict) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: ModelType, data: dict) -> None:
        for field, value in data.items():
            setattr(obj, field, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
