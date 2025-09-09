from pydantic import BaseModel

class DrawCategorySettingBase(BaseModel):
    draw_id: int
    category_id: int
    num_questions: int
    interval_minutes: int

class DrawCategorySettingCreate(DrawCategorySettingBase):
    pass

class DrawCategorySettingOut(DrawCategorySettingBase):
    setting_id: int

    class Config:
        orm_mode = True
