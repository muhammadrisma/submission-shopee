"""
Natural language query interface components for Streamlit.
Handles chat-style input, query history, and AI processing results.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from services.ai_query import get_ai_query_service, AIQueryService


class QueryInterface:
    """Handles natural language query interface and processing."""
    
    def __init__(self):
        """Initialize the query interface."""
        self.ai_service = get_ai_query_service()
        self.max_history = 50  # Maximum number of queries to keep in history
    
    def render_query_section(self):
        """
        Render the natural language query section with chat interface.
        """
        st.header("🤖 Ask About Your Receipts")
        st.write("Ask questions about your food purchases in natural language.")
        
        # Check if AI service is available
        if not self.ai_service:
            st.error("❌ AI query service is not available. Please check your OpenRouter API key configuration.")
            st.info("💡 Set your OPENROUTER_API_KEY in the .env file to enable natural language queries.")
            return
        
        # Initialize session state for query history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        # Query suggestions
        self._render_query_suggestions()
        
        # Main query input
        self._render_query_input()
        
        # Query history
        self._render_query_history()
    
    def _render_query_suggestions(self):
        """Render example query suggestions."""
        st.subheader("💡 Try These Examples")
        
        # Get base suggestions and add vector search examples
        base_suggestions = self.ai_service.get_query_suggestions()
        vector_suggestions = [
            "find chicken food",
            "search for apple fruit", 
            "similar to burrito",
            "mexican cuisine",
            "dairy products"
        ]
        
        suggestions = base_suggestions + vector_suggestions
        
        # Display suggestions in columns
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            col = cols[i % 2]
            with col:
                if st.button(f"💬 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                    # Set the suggestion as the current query
                    st.session_state.current_query = suggestion
                    st.rerun()
    
    def _render_query_input(self):
        """Render the main query input interface."""
        st.subheader("💬 Ask Your Question")
        
        # Text input for query
        query = st.text_input(
            "Enter your question:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., What food did I buy yesterday?",
            help="Ask questions about your food purchases, spending, or stores in natural language.",
            key="query_input"
        )
        
        # Clear the current_query after using it
        if 'current_query' in st.session_state:
            del st.session_state.current_query
        
        # Submit button
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_clicked = st.button("🔍 Ask", type="primary", use_container_width=True)
        
        with col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.query_history = []
                st.success("Query history cleared!")
                st.rerun()
        
        # Process query if submitted
        if submit_clicked and query.strip():
            self._process_query(query.strip())
    
    def _process_query(self, query: str):
        """
        Process a natural language query and display results.
        
        Args:
            query: The natural language query string
        """
        # Create loading indicators
        with st.spinner("🤔 Processing your query..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Parse query
                status_text.text("📝 Understanding your question...")
                progress_bar.progress(25)
                time.sleep(0.5)  # Brief pause for UX
                
                # Step 2: Search database
                status_text.text("🔍 Searching your receipts...")
                progress_bar.progress(50)
                
                # Process the query
                result = self.ai_service.process_query(query)
                
                # Step 3: Format response
                status_text.text("✨ Formatting response...")
                progress_bar.progress(75)
                time.sleep(0.3)
                
                # Step 4: Complete
                status_text.text("✅ Done!")
                progress_bar.progress(100)
                time.sleep(0.2)
                
                # Clear loading indicators
                progress_bar.empty()
                status_text.empty()
                
                # Add to history
                self._add_to_history(query, result)
                
                # Display result
                self._display_query_result(query, result)
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error processing query: {str(e)}")
    
    def _add_to_history(self, query: str, result: Dict[str, Any]):
        """Add query and result to session history."""
        history_item = {
            'timestamp': datetime.now(),
            'query': query,
            'result': result,
            'id': len(st.session_state.query_history)
        }
        
        # Add to beginning of history (most recent first)
        st.session_state.query_history.insert(0, history_item)
        
        # Limit history size
        if len(st.session_state.query_history) > self.max_history:
            st.session_state.query_history = st.session_state.query_history[:self.max_history]
    
    def _display_query_result(self, query: str, result: Dict[str, Any]):
        """
        Display the result of a query in a user-friendly format.
        
        Args:
            query: The original query string
            result: The processed result dictionary
        """
        st.subheader("💬 Response")
        
        if result['success']:
            # Display the formatted response
            st.write(result['formatted_response'])
            
            # Show vector search indicator if applicable
            if result['parsed_query']['intent'] == 'semantic_search':
                if result['results'] and 'similarity_score' in result['results'][0]:
                    top_similarity = result['results'][0]['similarity_score']
                    st.info(f"🔍 **Vector Search Used** - Top similarity: {top_similarity:.1%}")
                else:
                    st.info("🔍 **Vector Search Used** - No similar items found")
            
            # Show additional details in an expander
            with st.expander("📊 Query Details"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Processing Time", f"{result['execution_time']:.2f}s")
                    st.metric("Intent", result['parsed_query']['intent'].replace('_', ' ').title())
                
                with col2:
                    st.metric("Results Found", len(result['results']))
                    confidence = result['parsed_query'].get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.1%}")
                
                # Show similarity scores for vector search
                if result['parsed_query']['intent'] == 'semantic_search' and result['results']:
                    st.subheader("🎯 Similarity Scores")
                    for i, res in enumerate(result['results'][:5]):
                        if 'similarity_score' in res:
                            st.write(f"{i+1}. **{res['item_name']}**: {res['similarity_score']:.1%} similar")
                
                # Show raw results if available
                if result['results']:
                    st.subheader("Raw Data")
                    st.json(result['results'])
        else:
            # Display error
            st.error(result['formatted_response'])
            
            with st.expander("🔧 Error Details"):
                st.write(f"**Error:** {result.get('error', 'Unknown error')}")
                st.write(f"**Processing Time:** {result['execution_time']:.2f}s")
    
    def _render_query_history(self):
        """Render the query history section."""
        if not st.session_state.query_history:
            return
        
        st.subheader("📚 Query History")
        
        # Show recent queries
        for i, item in enumerate(st.session_state.query_history[:10]):  # Show last 10
            with st.expander(
                f"💬 {item['query'][:50]}{'...' if len(item['query']) > 50 else ''} "
                f"({item['timestamp'].strftime('%H:%M:%S')})"
            ):
                # Show query details
                st.write(f"**Query:** {item['query']}")
                st.write(f"**Time:** {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if item['result']['success']:
                    st.write(f"**Response:** {item['result']['formatted_response']}")
                    
                    # Quick stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Results", len(item['result']['results']))
                    with col2:
                        st.metric("Time", f"{item['result']['execution_time']:.2f}s")
                    with col3:
                        intent = item['result']['parsed_query']['intent']
                        st.metric("Intent", intent.replace('_', ' ').title())
                else:
                    st.error(f"**Error:** {item['result']['formatted_response']}")
                
                # Re-run button
                if st.button(f"🔄 Re-run Query", key=f"rerun_{item['id']}"):
                    self._process_query(item['query'])
    
    def render_query_stats(self):
        """Render query statistics and insights."""
        if not st.session_state.get('query_history'):
            return
        
        st.subheader("📈 Query Statistics")
        
        history = st.session_state.query_history
        
        # Basic stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", len(history))
        
        with col2:
            successful_queries = sum(1 for item in history if item['result']['success'])
            st.metric("Successful", successful_queries)
        
        with col3:
            if history:
                avg_time = sum(item['result']['execution_time'] for item in history) / len(history)
                st.metric("Avg Time", f"{avg_time:.2f}s")
            else:
                st.metric("Avg Time", "0.00s")
        
        with col4:
            if history:
                recent_queries = [item for item in history if 
                                (datetime.now() - item['timestamp']).seconds < 3600]  # Last hour
                st.metric("Last Hour", len(recent_queries))
            else:
                st.metric("Last Hour", "0")
        
        # Intent distribution
        if len(history) > 0:
            intent_counts = {}
            for item in history:
                if item['result']['success']:
                    intent = item['result']['parsed_query']['intent']
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            if intent_counts:
                st.subheader("🎯 Query Types")
                for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(history)) * 100
                    st.write(f"**{intent.replace('_', ' ').title()}:** {count} queries ({percentage:.1f}%)")


# Global query interface instance
query_interface = QueryInterface()