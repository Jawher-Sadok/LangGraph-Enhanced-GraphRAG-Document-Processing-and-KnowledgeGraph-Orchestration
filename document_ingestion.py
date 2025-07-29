# document_ingestion.py
from langgraph.graph import StateGraph
from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)

# Mock NER model (replace with your actual implementation)
class NERModel:
    @staticmethod
    def extract(text: str) -> Dict[str, List[str]]:
        # Simple mock implementation
        entities = {"ORG": [], "GPE": [], "PRODUCT": []}
        if "Apple Inc." in text:
            entities["ORG"].append("Apple Inc.")
        if "Cupertino" in text:
            entities["GPE"].extend(["American", "Cupertino", "California"])
        if "iPhone" in text:
            entities["PRODUCT"].extend(["iPhone", "iPad", "Mac", "Apple Watch"])
        return {k: v for k, v in entities.items() if v}

ner_model = NERModel()

# Relation extractor (replace with your actual implementation)
def relation_extractor(chunks: List[str]) -> List[Dict]:
    relations = []
    for chunk in chunks:
        if "Apple Inc." in chunk and "iPhone" in chunk:
            relations.append({
                "source": "Apple Inc.", 
                "target": "iPhone", 
                "relation": "manufactures"
            })
        if "Apple Inc." in chunk and "Cupertino" in chunk:
            relations.append({
                "source": "Apple Inc.", 
                "target": "Cupertino", 
                "relation": "headquartered_in"
            })
    return relations

class DocumentState(BaseModel):
    raw_text: str
    chunks: List[str] = []
    entities: Dict[str, List[str]] = {}
    relations: List[Dict] = []
    knowledge_graph: Dict = {}
    summary: Optional[str] = None

def chunk_document(state: DocumentState) -> DocumentState:
    if state.raw_text.strip():
        state.chunks = text_splitter.split_text(state.raw_text)
    else:
        state.chunks = [""]
    return state

def extract_entities(state: DocumentState) -> DocumentState:
    for chunk in state.chunks:
        entities = ner_model.extract(chunk)
        for key, values in entities.items():
            state.entities.setdefault(key, []).extend(values)
    return state

def build_relations(state: DocumentState) -> DocumentState:
    state.relations = relation_extractor(state.chunks)
    return state


# Build workflow
workflow = StateGraph(DocumentState)
workflow.add_node("chunk", chunk_document)
workflow.add_node("extract_entities", extract_entities)
workflow.add_node("build_relations", build_relations)
workflow.set_entry_point("chunk")
workflow.add_edge("chunk", "extract_entities")
workflow.add_edge("extract_entities", "build_relations")
workflow.set_finish_point("build_relations")

def run_workflow(text: str) -> DocumentState:
    """Helper function to run workflow and return DocumentState"""
    app = workflow.compile()
    result = app.invoke({"raw_text": text})
    return DocumentState(**result)  # Convert dict to DocumentState
