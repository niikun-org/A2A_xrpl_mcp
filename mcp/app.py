"""Gradio Web UI for MCP-Aware A2A Trace Logger

This application provides an interactive chat interface where:
1. Users chat with an AI assistant
2. AI can call MCP tools (all calls are logged)
3. Users can anchor the session logs to IPFS + XRPL
4. Full verification chain is maintained
"""

import os
import uuid
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

# Import MCP components
from .logger import get_logger
from .mcp_client import MCPClient
from .mcp_trace_builder import MCPTraceBuilder

# Import A2A anchor components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2a_anchor.anchor_service import create_anchor_service

# Load environment variables
load_dotenv()


class MCPChatApp:
    """Main application class for MCP chat with A2A anchoring."""

    def __init__(self):
        """Initialize the application."""
        self.logger = get_logger()
        self.mcp_client = MCPClient(
            server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        )

        # Check if MCP server is running
        if not self.mcp_client.health_check():
            print("⚠️  WARNING: MCP server is not running!")
            print("   Start it with: python -m mcp.mcp_server")

        # Initialize anchor service (lazy loading)
        self._anchor_service = None

    def get_anchor_service(self):
        """Get or create anchor service."""
        if self._anchor_service is None:
            ipfs_url = os.getenv("IPFS_API_URL", "http://127.0.0.1:5001")
            xrpl_node = os.getenv("XRPL_NODE_URL", "https://s.altnet.rippletest.net:51234")
            xrpl_seed = os.getenv("XRPL_SEED")

            if not xrpl_seed:
                raise ValueError("XRPL_SEED not set in environment!")

            self._anchor_service = create_anchor_service(
                ipfs_api_url=ipfs_url,
                xrpl_node_url=xrpl_node,
                xrpl_seed=xrpl_seed,
                xrpl_network="testnet"
            )

        return self._anchor_service

    def create_session(self) -> Dict[str, Any]:
        """Create a new chat session.

        Returns:
            Session state dictionary
        """
        return {
            "session_id": f"session-{uuid.uuid4().hex[:12]}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }

    def process_message(
        self,
        message: str,
        history: List[Tuple[str, str]],
        session_state: Dict[str, Any]
    ) -> Tuple[List[Tuple[str, str]], Dict[str, Any], str]:
        """Process a user message.

        Args:
            message: User input message
            history: Chat history
            session_state: Current session state

        Returns:
            Tuple of (updated_history, updated_state, stats_text)
        """
        session_id = session_state["session_id"]

        # Log user message
        self.logger.log_user_message(session_id, message)

        # Simple AI response with tool calling logic
        # Parse if user wants to use a tool
        response_text = self.generate_ai_response(session_id, message)

        # Log AI message
        self.logger.log_ai_message(session_id, response_text)

        # Update history
        history = history + [[message, response_text]]

        # Update session state
        session_state["messages"].append({
            "role": "user",
            "content": message
        })
        session_state["messages"].append({
            "role": "assistant",
            "content": response_text
        })

        # Get session stats
        stats = self.logger.get_session_stats(session_id)
        stats_text = self.format_stats(stats)

        return history, session_state, stats_text

    def generate_ai_response(self, session_id: str, user_message: str) -> str:
        """Generate AI response, potentially calling MCP tools.

        This is a simplified version. In production, this would use
        an actual LLM API (Claude, GPT, etc.)

        Args:
            session_id: Session ID
            user_message: User's message

        Returns:
            AI response text
        """
        msg_lower = user_message.lower()

        # Tool detection patterns
        if "calculate" in msg_lower or "compute" in msg_lower or any(op in msg_lower for op in ["+", "-", "*", "/"]):
            # Extract expression
            # Simple pattern matching for demo
            import re
            numbers_ops = re.findall(r'[\d\+\-\*/\(\)\.\s]+', user_message)
            if numbers_ops:
                expr = numbers_ops[0].strip()
                try:
                    result = self.mcp_client.call_tool_simple(
                        session_id, "calculate", expression=expr
                    )
                    return f"I calculated that for you: {result}"
                except Exception as e:
                    return f"I tried to calculate but got an error: {str(e)}"

        elif "time" in msg_lower or "date" in msg_lower:
            try:
                result = self.mcp_client.call_tool_simple(
                    session_id, "get_current_time"
                )
                return result
            except Exception as e:
                return f"Error getting time: {str(e)}"

        elif "count words" in msg_lower or "how many words" in msg_lower:
            # Extract text after the question
            text_to_count = user_message
            try:
                result = self.mcp_client.call_tool_simple(
                    session_id, "count_words", text=text_to_count
                )
                return result
            except Exception as e:
                return f"Error counting words: {str(e)}"

        elif "reverse" in msg_lower:
            # Extract text to reverse
            words = user_message.split()
            if len(words) > 1:
                text = " ".join(words[words.index("reverse")+1:]) if "reverse" in words else user_message
                try:
                    result = self.mcp_client.call_tool_simple(
                        session_id, "reverse_string", text=text
                    )
                    return f"Reversed: {result}"
                except Exception as e:
                    return f"Error reversing: {str(e)}"

        elif "palindrome" in msg_lower:
            # Extract text to check
            words = user_message.split()
            if len(words) > 1:
                text = " ".join(words[-3:])  # Last few words
                try:
                    result = self.mcp_client.call_tool_simple(
                        session_id, "check_palindrome", text=text
                    )
                    return result
                except Exception as e:
                    return f"Error checking palindrome: {str(e)}"

        # Default response
        return (
            f"I received your message: '{user_message}'. "
            "I can help you with calculations, time, word counting, "
            "string reversal, and palindrome checking. Try asking me to:\n"
            "- Calculate 2+2\n"
            "- What time is it?\n"
            "- Count words in this sentence\n"
            "- Reverse 'hello world'\n"
            "- Is 'racecar' a palindrome?"
        )

    def format_stats(self, stats: Dict[str, Any]) -> str:
        """Format session statistics for display.

        Args:
            stats: Statistics dictionary

        Returns:
            Formatted string
        """
        lines = [
            f"**Session Statistics**",
            f"- Session ID: `{stats['session_id']}`",
            f"- Total Events: {stats['event_count']}",
            f"- Tool Calls: {stats['tool_calls']}",
            f"- Errors: {stats['errors']}",
            f"- Total Latency: {stats['total_latency_ms']:.2f}ms"
        ]

        if stats['tools_used']:
            lines.append(f"- Tools Used: {', '.join(stats['tools_used'])}")

        return "\n".join(lines)

    def anchor_session(
        self,
        session_state: Dict[str, Any],
        model_name: str = "claude-3-5-sonnet-20241022"
    ) -> str:
        """Anchor session logs to IPFS + XRPL.

        Args:
            session_state: Session state
            model_name: Model name for trace

        Returns:
            Result message
        """
        session_id = session_state["session_id"]

        try:
            # Get session logs
            logs = self.logger.get_session_logs(session_id)

            if not logs:
                return "❌ No logs found for this session!"

            # Build A2A trace
            trace = MCPTraceBuilder.from_jsonl_logs(
                logs,
                model_name=model_name,
                provider="anthropic"
            )

            # Save local copy
            traces_dir = Path("traces")
            traces_dir.mkdir(exist_ok=True)
            trace_file = traces_dir / f"{session_id}.json"

            with open(trace_file, "w", encoding="utf-8") as f:
                f.write(trace.to_json())

            # Anchor to IPFS + XRPL
            anchor_service = self.get_anchor_service()
            result = anchor_service.anchor_trace(trace)

            # Format result
            output = [
                "✅ **Anchoring Complete!**\n",
                f"**Session ID:** `{result['session_id']}`",
                f"**IPFS CID:** `{result['cid']}`",
                f"**IPFS URL:** {result['ipfs_url']}",
                f"**XRPL TX Hash:** `{result['tx_hash']}`",
                f"**Ledger Index:** {result['ledger_index']}",
                f"**Merkle Root:** `{result['merkle_root'][:16]}...`",
                f"**Events:** {result['events_count']}",
                f"**Model:** {result['model']}",
                f"\n**Local File:** `{trace_file}`",
                f"\n**XRPL Explorer:**",
                f"https://testnet.xrpl.org/transactions/{result['tx_hash']}"
            ]

            return "\n".join(output)

        except Exception as e:
            return f"❌ **Anchoring Failed**\n\nError: {str(e)}"


def create_gradio_app() -> gr.Blocks:
    """Create and configure the Gradio application.

    Returns:
        Gradio Blocks app
    """
    app = MCPChatApp()

    with gr.Blocks(
        title="MCP-Aware A2A Trace Logger",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown("""
        # 🔗 MCP-Aware A2A Trace Logger

        ### Transparent & Verifiable AI Action Logging

        This demo shows how AI agent actions via MCP (Model Context Protocol) can be:
        - **Logged** in real-time (JSON-RPC format)
        - **Converted** to A2A trace format
        - **Anchored** to IPFS + XRPL for tamper-proof verification

        Try asking the AI to:
        - Calculate: "What is 25 * 4?"
        - Get time: "What time is it?"
        - Count words: "How many words in this sentence?"
        - Reverse text: "Reverse 'hello world'"
        - Check palindrome: "Is 'racecar' a palindrome?"
        """)

        # Session state
        session_state = gr.State(value=app.create_session())

        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat with AI (MCP Tools Enabled)",
                    height=400
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Your message",
                        placeholder="Ask me to calculate, check time, count words, etc.",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                clear_btn = gr.Button("Clear Chat")

            with gr.Column(scale=1):
                stats_display = gr.Markdown("*No session data yet*")

                gr.Markdown("### 🔒 Anchor to Blockchain")

                model_input = gr.Textbox(
                    label="Model Name",
                    value="claude-3-5-sonnet-20241022",
                    info="Model used for this conversation"
                )

                anchor_btn = gr.Button(
                    "⚓ Anchor Session Logs",
                    variant="primary",
                    size="lg"
                )

                anchor_result = gr.Markdown("*Not anchored yet*")

        # Event handlers
        def send_message(msg, history, state):
            if not msg.strip():
                return history, state, gr.Markdown("*No session data yet*")

            return app.process_message(msg, history, state)

        def clear_chat():
            new_state = app.create_session()
            return [], new_state, gr.Markdown("*Session reset*"), gr.Markdown("*Not anchored yet*")

        def anchor_logs(state, model_name):
            return app.anchor_session(state, model_name)

        # Wire up events
        msg_input.submit(
            send_message,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, session_state, stats_display]
        ).then(
            lambda: "",
            outputs=[msg_input]
        )

        send_btn.click(
            send_message,
            inputs=[msg_input, chatbot, session_state],
            outputs=[chatbot, session_state, stats_display]
        ).then(
            lambda: "",
            outputs=[msg_input]
        )

        clear_btn.click(
            clear_chat,
            outputs=[chatbot, session_state, stats_display, anchor_result]
        )

        anchor_btn.click(
            anchor_logs,
            inputs=[session_state, model_input],
            outputs=[anchor_result]
        )

        gr.Markdown("""
        ---
        ### 📚 How It Works

        1. **Chat**: Interact with the AI assistant
        2. **Tool Calls**: AI automatically uses MCP tools when needed
        3. **Logging**: All interactions are logged in `logs/events.jsonl`
        4. **Anchor**: Click "Anchor Session Logs" to:
           - Convert logs to A2A format
           - Compute Merkle Root
           - Upload to IPFS
           - Record on XRPL Testnet
        5. **Verify**: Use the XRPL Explorer link to verify the transaction

        Built for [MCP 1st Birthday Hackathon](https://huggingface.co/MCP-1st-Birthday)
        """)

    return demo


def main():
    """Main entry point."""
    print("="*70)
    print("MCP-Aware A2A Trace Logger - Gradio UI")
    print("="*70)

    # Check environment
    if not os.getenv("XRPL_SEED"):
        print("\n⚠️  WARNING: XRPL_SEED not set!")
        print("   Anchoring to XRPL will not work.")
        print("   Get a testnet account: https://xrpl.org/xrp-testnet-faucet.html")
        print("   Then add XRPL_SEED to .env file\n")

    demo = create_gradio_app()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
