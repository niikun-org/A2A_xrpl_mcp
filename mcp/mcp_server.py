"""MCP Server - Python Tools via JSON-RPC

This module provides a FastAPI-based MCP server that exposes tools
for AI agents to use via JSON-RPC protocol.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import math
import re

app = FastAPI(title="MCP A2A Trace Server")

# ========================================
# Tool Definitions
# ========================================

TOOLS = {
    "calculate": {
        "description": "Evaluate a mathematical expression safely",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2+2', '(5*3)/2')"
                }
            },
            "required": ["expression"]
        }
    },
    "get_current_time": {
        "description": "Get the current date and time in ISO format",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "count_words": {
        "description": "Count the number of words in a text",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to count words in"
                }
            },
            "required": ["text"]
        }
    },
    "reverse_string": {
        "description": "Reverse a string",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to reverse"
                }
            },
            "required": ["text"]
        }
    },
    "check_palindrome": {
        "description": "Check if a text is a palindrome (reads the same forwards and backwards)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to check"
                }
            },
            "required": ["text"]
        }
    }
}

# ========================================
# Tool Implementations
# ========================================

def safe_eval(expression: str) -> float:
    """Safely evaluate a mathematical expression.

    Only allows basic math operations: +, -, *, /, **, (), and numbers.
    """
    # Remove whitespace
    expression = expression.replace(" ", "")

    # Check for dangerous patterns
    dangerous_patterns = [
        r'__',  # dunder methods
        r'import',
        r'exec',
        r'eval',
        r'compile',
        r'open',
        r'file',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            raise ValueError(f"Forbidden pattern detected: {pattern}")

    # Only allow safe characters
    allowed_chars = set('0123456789+-*/().**. ')
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expression contains forbidden characters")

    # Evaluate in restricted namespace
    allowed_names = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return float(result)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {str(e)}")


def execute_tool(name: str, arguments: dict) -> dict:
    """Execute a tool by name with given arguments.

    Returns:
        dict: Result in MCP format with 'content' array
    """
    try:
        if name == "calculate":
            expression = arguments.get("expression", "")
            result = safe_eval(expression)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Result: {result}"
                }]
            }

        elif name == "get_current_time":
            current_time = datetime.now().isoformat()
            return {
                "content": [{
                    "type": "text",
                    "text": f"Current time: {current_time}"
                }]
            }

        elif name == "count_words":
            text = arguments.get("text", "")
            word_count = len(text.split())
            return {
                "content": [{
                    "type": "text",
                    "text": f"Word count: {word_count}"
                }]
            }

        elif name == "reverse_string":
            text = arguments.get("text", "")
            reversed_text = text[::-1]
            return {
                "content": [{
                    "type": "text",
                    "text": reversed_text
                }]
            }

        elif name == "check_palindrome":
            text = arguments.get("text", "")
            # Normalize: lowercase and remove non-alphanumeric
            normalized = re.sub(r'[^a-z0-9]', '', text.lower())
            is_palindrome = normalized == normalized[::-1]

            return {
                "content": [{
                    "type": "text",
                    "text": f"'{text}' is {'a palindrome' if is_palindrome else 'not a palindrome'}"
                }]
            }

        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: Unknown tool '{name}'"
                }],
                "isError": True
            }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error executing tool: {str(e)}"
            }],
            "isError": True
        }


# ========================================
# JSON-RPC Endpoints
# ========================================

@app.post("/")
async def handle_jsonrpc(request: Request):
    """Handle JSON-RPC requests for MCP protocol.

    Supports:
    - tools/list: List all available tools
    - tools/call: Execute a specific tool
    """
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": str(e)
            },
            "id": None
        })

    method = data.get("method")
    request_id = data.get("id", 1)

    # tools/list - List all available tools
    if method == "tools/list":
        tools_list = [
            {"name": name, **info}
            for name, info in TOOLS.items()
        ]

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "tools": tools_list
            },
            "id": request_id
        })

    # tools/call - Execute a tool
    elif method == "tools/call":
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Invalid params: missing 'name'"
                },
                "id": request_id
            })

        if tool_name not in TOOLS:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                },
                "id": request_id
            })

        # Execute tool
        result = execute_tool(tool_name, arguments)

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })

    # Unknown method
    else:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            },
            "id": request_id
        })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "tools_count": len(TOOLS)}


if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("MCP A2A Trace Server")
    print("="*70)
    print(f"Available tools: {', '.join(TOOLS.keys())}")
    print("Starting server on http://0.0.0.0:8000")
    print("="*70)
    uvicorn.run(app, host="0.0.0.0", port=8000)
