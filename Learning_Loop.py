from langgraph.graph import StateGraph

class LearningState(BaseModel):
    queries: List[str] = []
    responses: List[str] = []
    new_entities: Dict = {}
    feedback: Dict = {}

def process_feedback(state: LearningState):
    # Analyze user feedback to improve KG
    for fb in state.feedback:
        if fb['correct'] is False:
            kg.update_with_feedback(fb)
    return state

learning_workflow = StateGraph(LearningState)
learning_workflow.add_node("process", process_feedback)
learning_workflow.set_entry_point("process")
learning_workflow.set_finish_point("process")