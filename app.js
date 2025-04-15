document.addEventListener('DOMContentLoaded', function() {
    // State to track workflow nodes
    let workflowNodes = [];
    let selectedNodeIndex = -1;
    let currentWorkflowId = null;
    
    // DOM Elements
    const workflowNameInput = document.getElementById('workflow-name');
    const nodeTypeSelect = document.getElementById('node-type');
    const addNodeBtn = document.getElementById('add-node-btn');
    const nodesList = document.getElementById('nodes-list');
    const generateWorkflowBtn = document.getElementById('generate-workflow-btn');
    const workflowJsonPreview = document.getElementById('workflow-json');
    const aiGenerateBtn = document.getElementById('ai-generate-btn');
    const workflowDescription = document.getElementById('workflow-description');
    
    // Event Listeners
    addNodeBtn.addEventListener('click', addNode);
    generateWorkflowBtn.addEventListener('click', generateWorkflow);
    aiGenerateBtn.addEventListener('click', generateWorkflowFromDescription);
    
    // Function to add a new node
    function addNode() {
        const nodeType = nodeTypeSelect.value;
        const nodeConfig = createDefaultNodeConfig(nodeType);
        
        workflowNodes.push(nodeConfig);
        renderNodesList();
        updateWorkflowPreview();
    }
    
    // Create default configuration for different node types
    function createDefaultNodeConfig(nodeType) {
        const nodeId = `node_${Date.now()}`;
        
        switch(nodeType) {
            case 'http':
                return {
                    id: nodeId,
                    type: 'http',
                    name: 'HTTP Request',
                    parameters: {
                        url: 'https://example.com/api',
                        method: 'GET',
                        headers: {}
                    }
                };
            case 'function':
                return {
                    id: nodeId,
                    type: 'function',
                    name: 'Function',
                    parameters: {
                        code: 'return items;'
                    }
                };
            case 'webhook':
                return {
                    id: nodeId,
                    type: 'webhook',
                    name: 'Webhook',
                    parameters: {
                        path: '/webhook',
                        method: 'POST'
                    }
                };
            case 'schedule':
                return {
                    id: nodeId,
                    type: 'schedule',
                    name: 'Schedule',
                    parameters: {
                        frequency: 'hourly'
                    }
                };
            default:
                return {
                    id: nodeId,
                    type: nodeType,
                    name: nodeType.charAt(0).toUpperCase() + nodeType.slice(1),
                    parameters: {}
                };
        }
    }
    
    // Render the nodes list in the sidebar
    function renderNodesList() {
        nodesList.innerHTML = '';
        
        workflowNodes.forEach((node, index) => {
            const nodeItem = document.createElement('div');
            nodeItem.className = `node-item ${selectedNodeIndex === index ? 'selected' : ''}`;
            nodeItem.dataset.index = index;
            
            nodeItem.innerHTML = `
                <h4>
                    ${node.name} (${node.type})
                    <div class="node-controls">
                        <button class="node-control-btn edit-node" data-index="${index}">Edit</button>
                        <button class="node-control-btn delete-node" data-index="${index}">Delete</button>
                    </div>
                </h4>
                <div class="node-details">
                    <small>ID: ${node.id}</small>
                </div>
            `;
            
            nodeItem.addEventListener('click', function() {
                selectNode(index);
            });
            
            nodesList.appendChild(nodeItem);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-node').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.index);
                editNode(index);
            });
        });
        
        document.querySelectorAll('.delete-node').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.index);
                deleteNode(index);
            });
        });
    }
    
    // Select a node
    function selectNode(index) {
        selectedNodeIndex = index;
        renderNodesList();
    }
    
    // Edit a node (placeholder for now)
    function editNode(index) {
        // In a more complex implementation, this would open a modal or form
        // For now, we'll just show an alert
        alert(`Editing node: ${workflowNodes[index].name}`);
        
        // Future enhancement: Show a form with the node's parameters
    }
    
    // Delete a node
    function deleteNode(index) {
        if (confirm(`Are you sure you want to delete the node "${workflowNodes[index].name}"?`)) {
            workflowNodes.splice(index, 1);
            
            if (selectedNodeIndex === index) {
                selectedNodeIndex = -1;
            } else if (selectedNodeIndex > index) {
                selectedNodeIndex--;
            }
            
            renderNodesList();
            updateWorkflowPreview();
        }
    }
    
    // Generate and display the workflow JSON
    function generateWorkflow() {
        const workflowName = workflowNameInput.value || 'My Workflow';
        
        const workflow = {
            name: workflowName,
            nodes: workflowNodes,
            connections: generateConnections()
        };
        
        updateWorkflowPreview(workflow);
        
        // Send the workflow to the API
        saveWorkflow(workflow);
    }
    
    // Save workflow to API
    async function saveWorkflow(workflow) {
        try {
            const method = currentWorkflowId ? 'PUT' : 'POST';
            const url = currentWorkflowId 
                ? `/api/workflows/${currentWorkflowId}` 
                : '/api/workflows/';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(workflow)
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!currentWorkflowId) {
                currentWorkflowId = Object.keys(data)[0];
                alert(`Workflow saved with ID: ${currentWorkflowId}`);
            } else {
                alert('Workflow updated successfully');
            }
        } catch (error) {
            console.error('Error saving workflow:', error);
            alert(`Error saving workflow: ${error.message}`);
        }
    }
    
    // Generate connections between nodes (simple linear flow for now)
    function generateConnections() {
        const connections = [];
        
        for (let i = 0; i < workflowNodes.length - 1; i++) {
            connections.push({
                source: workflowNodes[i].id,
                target: workflowNodes[i + 1].id
            });
        }
        
        return connections;
    }
    
    // Update the workflow preview in the code panel
    function updateWorkflowPreview(workflow) {
        if (!workflow) {
            const workflowName = workflowNameInput.value || 'My Workflow';
            
            workflow = {
                name: workflowName,
                nodes: workflowNodes,
                connections: generateConnections()
            };
        }
        
        workflowJsonPreview.textContent = JSON.stringify(workflow, null, 2);
    }
    
    // Initialize the interface
    function init() {
        updateWorkflowPreview();
    }
    
    // Start the application
    init();
    
    // Add this new function to generate workflows from natural language
    async function generateWorkflowFromDescription() {
        const description = workflowDescription.value.trim();
        
        if (!description) {
            alert('Please enter a workflow description');
            return;
        }
        
        try {
            // Show loading state
            aiGenerateBtn.disabled = true;
            aiGenerateBtn.textContent = 'Generating...';
            
            // Call the API to generate workflow
            const response = await fetch('/api/generate-workflow/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ description })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const generatedWorkflow = await response.json();
            
            // Apply the generated workflow
            workflowNameInput.value = generatedWorkflow.name;
            workflowNodes = generatedWorkflow.nodes;
            
            renderNodesList();
            updateWorkflowPreview();
            
            // Scroll to the nodes list
            nodesList.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error generating workflow:', error);
            alert(`Error generating workflow: ${error.message}`);
        } finally {
            // Reset button state
            aiGenerateBtn.disabled = false;
            aiGenerateBtn.textContent = 'Generate with AI';
        }
    }
}); 