from typing import Type, TypeVar, Generic, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    ALLOWED_SEARCH_FIELDS: set[str] = set()

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        return self.db.get(self.model, id)
    
    def list(self) -> list[ModelType]:
        stmt = select(self.model)
        return self.db.execute(stmt).scalars().all()
    
    def create(self, data: dict, commit: bool = True):
        obj = self.model(**data)
        self.db.add(obj)
        if commit:
            self.db.commit()
            self.db.refresh(obj)
        else:
            self.db.flush()
        return obj
    
    def update(self, obj: ModelType, data: dict) -> ModelType:
        for field, value in data.items():
            setattr(obj, field, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
    
    def filter(self, **filters) -> List[ModelType]:
        conditions = []

        for field, value in filters.items():
            if field in self.ALLOWED_SEARCH_FIELDS and value is not None:
                column = getattr(self.model, field, None)
                if column is not None:
                    conditions.append(column == value)

        stmt = select(self.model)

        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        if filters and not conditions:
            return []

        return self.db.execute(stmt).scalars().all()
