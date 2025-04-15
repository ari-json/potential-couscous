from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import uuid
import openai
from dotenv import load_dotenv
from ai_processor import process_description
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="n8n Workflow Composer API",
    description="API for creating and managing n8n workflows",
    version="1.0.0"
)

# Load environment variables
load_dotenv()

# Set up OpenAI (optional - alternatively you can use your own language model)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define models
class NodeParameter(BaseModel):
    url: Optional[str] = None
    method: Optional[str] = None
    code: Optional[str] = None
    path: Optional[str] = None
    frequency: Optional[str] = None
    headers: Optional[Dict[str, str]] = {}

class Node(BaseModel):
    id: str
    type: str
    name: str
    parameters: NodeParameter

class Connection(BaseModel):
    source: str
    target: str

class Workflow(BaseModel):
    name: str
    nodes: List[Node]
    connections: List[Connection]

# Storage for workflows (in-memory for this example)
workflows = {}

# Create workflow
@app.post("/api/workflows/", response_model=Workflow, tags=["Workflows"])
async def create_workflow(workflow: Workflow):
    workflow_id = str(uuid.uuid4())
    workflows[workflow_id] = workflow
    return workflow

# Get all workflows
@app.get("/api/workflows/", response_model=Dict[str, Workflow], tags=["Workflows"])
async def get_workflows():
    return workflows

# Get workflow by ID
@app.get("/api/workflows/{workflow_id}", response_model=Workflow, tags=["Workflows"])
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]

# Update workflow
@app.put("/api/workflows/{workflow_id}", response_model=Workflow, tags=["Workflows"])
async def update_workflow(workflow_id: str, workflow: Workflow):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflows[workflow_id] = workflow
    return workflow

# Delete workflow
@app.delete("/api/workflows/{workflow_id}", tags=["Workflows"])
async def delete_workflow(workflow_id: str):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    del workflows[workflow_id]
    return {"message": "Workflow deleted"}

# Update your generate workflow endpoint
@app.post("/api/generate-workflow/", response_model=Workflow, tags=["AI"])
async def generate_workflow_from_description(
    request: dict = None,
    description: str = Query(None, description="Workflow description in natural language")
):
    # Get description from query parameter or request body
    desc = description
    
    # If no query parameter but body exists
    if not desc and request and "description" in request:
        desc = request.get("description")
    
    if not desc:
        raise HTTPException(status_code=400, detail="Workflow description is required (provide in query or body)")
    
    try:
        # Call AI to generate workflow structure
        workflow = await generate_workflow_with_ai(desc)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_workflow_with_ai(description: str) -> Workflow:
    """Generate a workflow structure based on a natural language description."""
    
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Use rule-based fallback if no API key
        print("OpenAI API key not found. Using rule-based generation.")
        workflow_data = process_description(description)
        return Workflow(**workflow_data)
    
    # Define a system prompt that explains the task to the AI
    system_prompt = """
    You are an expert n8n workflow designer. Your task is to create a workflow based on a description.
    Output a JSON structure that represents an n8n workflow with the following format:
    {
        "name": "Workflow name",
        "nodes": [
            {
                "id": "node_id",
                "type": "node_type", 
                "name": "Node Name",
                "parameters": {...}
            }
        ],
        "connections": [
            {
                "source": "source_node_id",
                "target": "target_node_id"
            }
        ]
    }
    
    Only return valid JSON. Support these node types: http, function, webhook, schedule.
    """
    
    # Generate the workflow using AI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a workflow based on this description: {description}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        workflow_json = response.choices[0].message.content.strip()
        
        # Extract just the JSON portion if there's any explanation text
        import re
        json_match = re.search(r'({.*})', workflow_json, re.DOTALL)
        if json_match:
            workflow_json = json_match.group(1)
        
        # Parse the generated JSON
        workflow_data = json.loads(workflow_json)
        
        # Ensure basic structure is correct
        if not all(key in workflow_data for key in ("name", "nodes", "connections")):
            raise ValueError("Generated workflow is missing required components")
        
        # Create and validate the Workflow model
        workflow = Workflow(**workflow_data)
        return workflow
        
    except Exception as e:
        raise ValueError(f"Failed to generate workflow: {str(e)}")

# Serve static files (your HTML/CSS/JS frontend)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run server if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    print("Starting API server...")
    port = int(os.getenv("PORT", "8000"))
    print(f"Using port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 