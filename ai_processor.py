def process_description(description: str):
    """
    A simple rule-based system to create workflows from descriptions
    """
    description = description.lower()
    nodes = []
    connections = []
    
    # Set a default workflow name
    workflow_name = "Generated Workflow"
    
    # Extract workflow name if mentioned
    if "create a workflow" in description and "called" in description:
        name_match = re.search(r'called\s+["\']?([^"\']+)["\']?', description)
        if name_match:
            workflow_name = name_match.group(1)
    
    # Add trigger node based on keywords
    trigger_node_id = f"node_{int(time.time())}"
    if "every hour" in description or "hourly" in description:
        nodes.append({
            "id": trigger_node_id,
            "type": "schedule",
            "name": "Schedule Trigger",
            "parameters": {"frequency": "hourly"}
        })
    elif "webhook" in description or "api call" in description:
        nodes.append({
            "id": trigger_node_id,
            "type": "webhook",
            "name": "Webhook Trigger",
            "parameters": {"path": "/webhook", "method": "POST"}
        })
    else:
        # Default trigger
        nodes.append({
            "id": trigger_node_id,
            "type": "schedule",
            "name": "Manual Trigger",
            "parameters": {"frequency": "manual"}
        })
    
    # Add action nodes based on keywords
    last_node_id = trigger_node_id
    
    # Add HTTP request if mentioned
    if any(keyword in description for keyword in ["fetch", "get data", "api", "request"]):
        http_node_id = f"node_{int(time.time()) + 1}"
        nodes.append({
            "id": http_node_id,
            "type": "http",
            "name": "HTTP Request",
            "parameters": {"url": "https://api.example.com/data", "method": "GET"}
        })
        connections.append({"source": last_node_id, "target": http_node_id})
        last_node_id = http_node_id
    
    # Add function if processing is mentioned
    if any(keyword in description for keyword in ["process", "transform", "filter", "map"]):
        function_node_id = f"node_{int(time.time()) + 2}"
        nodes.append({
            "id": function_node_id,
            "type": "function",
            "name": "Process Data",
            "parameters": {"code": "// Transform the data\nreturn items.map(item => {\n  return item;\n});"}
        })
        connections.append({"source": last_node_id, "target": function_node_id})
    
    return {
        "name": workflow_name,
        "nodes": nodes,
        "connections": connections
    } 