from pydantic import BaseModel


class OpinionCreate(BaseModel):
    question_round_id: int
    selected_product_id: int
    opposite_product_id: int
    category_id: int
    reason_id: int
