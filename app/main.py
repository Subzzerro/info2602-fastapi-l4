import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from app.database import SessionDep
from app.models import Category, Todo, RegularUser, CategoryResponse, TodoResponse
from app.auth import AuthDep

app = FastAPI()

@app.post("/category", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryResponse, db: SessionDep, user: RegularUser = Depends(AuthDep)):
    new_category = Category(text=category.text, user_id=user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.post("/todo/{todo_id}/category/{cat_id}")
def add_category_to_todo(todo_id: int, cat_id: int, db: SessionDep, user: RegularUser = Depends(AuthDep)):
    todo = db.get(Todo, todo_id)
    category = db.get(Category, cat_id)
    if not todo or not category:
        raise HTTPException(status_code=404, detail="Todo or Category not found")
    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if category not in todo.categories:
        todo.categories.append(category)
        db.add(todo)
        db.commit()
    return {"message": f"Category '{category.text}' added to todo '{todo.text}'"}

@app.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category_from_todo(todo_id: int, cat_id: int, db: SessionDep, user: RegularUser = Depends(AuthDep)):
    todo = db.get(Todo, todo_id)
    category = db.get(Category, cat_id)
    if not todo or not category:
        raise HTTPException(status_code=404, detail="Todo or Category not found")
    if todo.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if category in todo.categories:
        todo.categories.remove(category)
        db.add(todo)
        db.commit()
    return {"message": f"Category '{category.text}' removed from todo '{todo.text}'"}

@app.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, db: SessionDep, user: RegularUser = Depends(AuthDep)):
    category = db.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return category.todos

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
