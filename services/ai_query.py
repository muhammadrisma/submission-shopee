"""
AI Query Service for natural language processing of receipt queries.
Integrates with OpenRouter's DeepSeek Chat v3.1 model for query understanding and response generation.
"""

import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import requests

from config import config
from database.service import db_service
from models.receipt import Receipt, ReceiptItem
from services.vector_db import vector_db


class OpenRouterClient:
    """Client for OpenRouter API integration."""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model: str = "deepseek/deepseek-chat"):
        """Initialize the OpenRouter client."""
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/food-receipt-analyzer",
            "X-Title": "Food Receipt Analyzer"
        }
    
    def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.1) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse OpenRouter API response: {e}")
        except Exception as e:
            raise Exception(f"OpenRouter API request failed: {e}")


class QueryParser:
    """Parser for extracting intent and parameters from natural language queries."""
    
    def __init__(self):
        """Initialize the query parser with patterns."""
        self.semantic_keywords = {
            'similar', 'like', 'related', 'comparable', 'resembling',
            'find', 'search', 'look', 'discover', 'match'
        }
        self.date_patterns = {
            'yesterday': lambda: date.today() - timedelta(days=1),
            'today': lambda: date.today(),
            'last week': lambda: (date.today() - timedelta(days=7), date.today()),
            'last 7 days': lambda: (date.today() - timedelta(days=7), date.today()),
            'this week': lambda: self._get_week_range(),
            'this month': lambda: self._get_month_range()
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query and extract intent and parameters.
        Returns a dictionary with query type, parameters, and metadata.
        """
        query_lower = query.lower().strip()
        
        # Check for semantic search intent first
        if any(word in query_lower for word in self.semantic_keywords):
            return self._parse_semantic_query(query_lower)
        
        # Determine query intent
        if any(word in query_lower for word in ['what', 'which', 'show', 'list']):
            if any(word in query_lower for word in ['buy', 'bought', 'purchase', 'food', 'item']):
                return self._parse_item_query(query_lower)
        
        if any(word in query_lower for word in ['total', 'spend', 'spent', 'cost', 'expense']):
            return self._parse_spending_query(query_lower)
        
        if any(word in query_lower for word in ['where', 'store', 'shop']):
            return self._parse_store_query(query_lower)
        
        # Default fallback
        # Check if this might be a semantic search query
        if len(query_lower.split()) <= 5:  # Short queries are likely semantic
            return {
                'intent': 'semantic_search',
                'query': query,
                'parameters': {'search_term': query_lower},
                'confidence': 0.6
            }
        
        return {
            'intent': 'general',
            'query': query,
            'parameters': {},
            'confidence': 0.3
        }
    
    def _parse_item_query(self, query: str) -> Dict[str, Any]:
        """Parse queries asking about items purchased."""
        date_info = self._extract_date_info(query)
        
        return {
            'intent': 'list_items',
            'query': query,
            'parameters': {
                'date_range': date_info.get('date_range'),
                'specific_date': date_info.get('specific_date'),
                'days_back': date_info.get('days_back')
            },
            'confidence': 0.8
        }
    
    def _parse_spending_query(self, query: str) -> Dict[str, Any]:
        """Parse queries asking about spending/costs."""
        date_info = self._extract_date_info(query)
        
        return {
            'intent': 'total_spending',
            'query': query,
            'parameters': {
                'date_range': date_info.get('date_range'),
                'specific_date': date_info.get('specific_date'),
                'days_back': date_info.get('days_back')
            },
            'confidence': 0.9
        }
    
    def _parse_store_query(self, query: str) -> Dict[str, Any]:
        """Parse queries asking about stores."""
        date_info = self._extract_date_info(query)
        item_name = self._extract_item_name(query)
        
        return {
            'intent': 'find_stores',
            'query': query,
            'parameters': {
                'item_name': item_name,
                'date_range': date_info.get('date_range'),
                'specific_date': date_info.get('specific_date'),
                'days_back': date_info.get('days_back')
            },
            'confidence': 0.8
        }
    
    def _parse_semantic_query(self, query: str) -> Dict[str, Any]:
        """Parse queries asking for semantic similarity."""
        # Extract the item/concept they're looking for
        search_term = query
        
        # Remove semantic keywords to get the core search term
        for keyword in self.semantic_keywords:
            search_term = search_term.replace(keyword, '').strip()
        
        # Remove common words
        common_words = ['to', 'for', 'items', 'food', 'things', 'stuff']
        for word in common_words:
            search_term = search_term.replace(word, '').strip()
        
        date_info = self._extract_date_info(query)
        
        return {
            'intent': 'semantic_search',
            'query': query,
            'parameters': {
                'search_term': search_term,
                'date_range': date_info.get('date_range'),
                'specific_date': date_info.get('specific_date'),
                'days_back': date_info.get('days_back')
            },
            'confidence': 0.9
        }
    
    def _extract_date_info(self, query: str) -> Dict[str, Any]:
        """Extract date information from query."""
        result = {}
        
        # Check for "last X days" pattern first (more specific)
        days_match = re.search(r'last\s+(\d+)\s+days?', query)
        if days_match:
            days = int(days_match.group(1))
            result['days_back'] = days
            return result
        
        # Check for "from last X days" pattern
        from_days_match = re.search(r'from\s+last\s+(\d+)\s+days?', query)
        if from_days_match:
            days = int(from_days_match.group(1))
            result['days_back'] = days
            return result
        
        # Check for year patterns like "in 2018", "from 2018"
        year_match = re.search(r'(?:in|from)\s+(\d{4})', query)
        if year_match:
            year = int(year_match.group(1))
            try:
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)
                result['date_range'] = (start_date, end_date)
                return result
            except ValueError:
                pass
        
        # Check for relative date patterns
        for pattern, date_func in self.date_patterns.items():
            if pattern in query:
                date_result = date_func()
                if isinstance(date_result, tuple):
                    result['date_range'] = date_result
                else:
                    result['specific_date'] = date_result
                return result
        
        # Check for specific date patterns (e.g., "20 June", "June 20", "2024-06-20")
        date_match = re.search(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)', query, re.IGNORECASE)
        if date_match:
            day = int(date_match.group(1))
            month_name = date_match.group(2).lower()
            month_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            month = month_map.get(month_name)
            if month:
                try:
                    # Assume current year if not specified
                    target_date = date(date.today().year, month, day)
                    result['specific_date'] = target_date
                    return result
                except ValueError:
                    pass
        

        
        return result
    
    def _extract_item_name(self, query: str) -> Optional[str]:
        """Extract item name from query."""
        # Look for patterns like "buy hamburger", "bought pizza", etc.
        item_patterns = [
            r'buy\s+(\w+)',
            r'bought\s+(\w+)',
            r'purchase[d]?\s+(\w+)',
            r'purchases\s+of\s+(\w+)',
            r'get\s+(\w+)',
            r'got\s+(\w+)'
        ]
        
        for pattern in item_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_week_range(self) -> Tuple[date, date]:
        """Get the current week date range (Monday to Sunday)."""
        today = date.today()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        return (monday, sunday)
    
    def _get_month_range(self) -> Tuple[date, date]:
        """Get the current month date range."""
        today = date.today()
        first_day = date(today.year, today.month, 1)
        if today.month == 12:
            last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return (first_day, last_day)

class SQLQueryGenerator:
    """Generates SQL queries based on parsed natural language queries."""
    
    def __init__(self, db_service):
        """Initialize with database service."""
        self.db_service = db_service
    
    def generate_query_results(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate and execute appropriate database queries based on parsed intent."""
        intent = parsed_query['intent']
        params = parsed_query['parameters']
        
        if intent == 'list_items':
            return self._query_items(params)
        elif intent == 'total_spending':
            return self._query_spending(params)
        elif intent == 'find_stores':
            return self._query_stores(params)
        elif intent == 'semantic_search':
            return self._query_semantic(params)
        else:
            return []
    
    def _query_items(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query for items based on date parameters."""
        if params.get('specific_date'):
            receipts = self.db_service.get_receipts_by_date_range(
                params['specific_date'], 
                params['specific_date']
            )
            items = []
            for receipt in receipts:
                for item in receipt.items:
                    items.append({
                        'item_name': item.item_name,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'store_name': receipt.store_name,
                        'receipt_date': receipt.receipt_date
                    })
            return items
        
        elif params.get('date_range'):
            start_date, end_date = params['date_range']
            receipts = self.db_service.get_receipts_by_date_range(start_date, end_date)
            items = []
            for receipt in receipts:
                for item in receipt.items:
                    items.append({
                        'item_name': item.item_name,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'store_name': receipt.store_name,
                        'receipt_date': receipt.receipt_date
                    })
            return items
        
        elif params.get('days_back'):
            # Get all items from the last N days
            end_date = date.today()
            start_date = end_date - timedelta(days=params['days_back'])
            receipts = self.db_service.get_receipts_by_date_range(start_date, end_date)
            items = []
            for receipt in receipts:
                for item in receipt.items:
                    items.append({
                        'item_name': item.item_name,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'store_name': receipt.store_name,
                        'receipt_date': receipt.receipt_date
                    })
            return items
        
        # Fallback: if no date parameters, return all items
        receipts = self.db_service.get_all_receipts()
        items = []
        for receipt in receipts:
            for item in receipt.items:
                items.append({
                    'item_name': item.item_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                    'store_name': receipt.store_name,
                    'receipt_date': receipt.receipt_date
                })
        return items
    
    def _query_spending(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query for spending totals based on date parameters."""
        if params.get('specific_date'):
            total = self.db_service.get_total_spending_by_date(params['specific_date'])
            return [{
                'total_spending': total,
                'date': params['specific_date'],
                'type': 'daily_total'
            }]
        
        elif params.get('date_range'):
            start_date, end_date = params['date_range']
            receipts = self.db_service.get_receipts_by_date_range(start_date, end_date)
            total = sum(receipt.total_amount for receipt in receipts)
            return [{
                'total_spending': total,
                'start_date': start_date,
                'end_date': end_date,
                'type': 'range_total'
            }]
        
        elif params.get('days_back'):
            end_date = date.today()
            start_date = end_date - timedelta(days=params['days_back'])
            receipts = self.db_service.get_receipts_by_date_range(start_date, end_date)
            total = sum(receipt.total_amount for receipt in receipts)
            return [{
                'total_spending': total,
                'start_date': start_date,
                'end_date': end_date,
                'days_back': params['days_back'],
                'type': 'days_back_total'
            }]
        
        return []
    
    def _query_stores(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query for stores based on item and date parameters."""
        item_name = params.get('item_name')
        days_back = params.get('days_back')
        
        if item_name:
            stores = self.db_service.get_stores_with_item(item_name, days_back)
            return [{
                'stores': stores,
                'item_name': item_name,
                'days_back': days_back,
                'type': 'stores_with_item'
            }]
        
        return []
    
    def _query_semantic(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query using semantic similarity search."""
        search_term = params.get('search_term', '')
        if not search_term:
            return []
        
        # Ensure vector index is built
        stats = vector_db.get_stats()
        if stats['vector_count'] == 0:
            vector_db.build_index()
        
        # Perform semantic search
        results = vector_db.semantic_search(search_term, top_k=10)
        
        # Convert to standard format
        formatted_results = []
        for result in results:
            formatted_results.append({
                'item_name': result.item_name,
                'quantity': 1,  # Default quantity
                'unit_price': result.metadata.get('price', 0),
                'total_price': result.metadata.get('price', 0),
                'store_name': result.metadata.get('store_name', 'Unknown'),
                'receipt_date': datetime.fromisoformat(result.metadata.get('receipt_date', '2024-01-01')).date(),
                'similarity_score': result.similarity_score
            })
        
        return formatted_results


class ResponseFormatter:
    """Formats database results into natural language responses."""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize with OpenRouter client for AI-powered formatting."""
        self.client = openrouter_client
    
    def format_response(self, query: str, results: List[Dict[str, Any]], parsed_query: Dict[str, Any]) -> str:
        """Format database results into a natural language response."""
        if not results:
            return self._format_no_results_response(query, parsed_query)
        
        intent = parsed_query['intent']
        
        if intent == 'list_items':
            return self._format_items_response(results, query)
        elif intent == 'total_spending':
            return self._format_spending_response(results, query)
        elif intent == 'find_stores':
            return self._format_stores_response(results, query)
        elif intent == 'semantic_search':
            return self._format_semantic_response(results, query)
        else:
            return self._format_general_response(results, query)
    
    def _format_items_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format items list response."""
        if len(results) == 0:
            return "I couldn't find any food items matching your query."
        
        # Group items by date for better presentation
        items_by_date = {}
        for item in results:
            date_key = item['receipt_date']
            if date_key not in items_by_date:
                items_by_date[date_key] = []
            items_by_date[date_key].append(item)
        
        response_parts = []
        total_items = len(results)
        
        if len(items_by_date) == 1:
            # Single date
            date_key = list(items_by_date.keys())[0]
            response_parts.append(f"On {date_key.strftime('%B %d, %Y')}, you bought:")
            for item in items_by_date[date_key]:
                response_parts.append(f"• {item['item_name']} (${item['total_price']:.2f}) from {item['store_name']}")
        else:
            # Multiple dates
            response_parts.append(f"Here are the {total_items} food items you bought:")
            for date_key in sorted(items_by_date.keys(), reverse=True):
                response_parts.append(f"\n{date_key.strftime('%B %d, %Y')}:")
                for item in items_by_date[date_key]:
                    response_parts.append(f"• {item['item_name']} (${item['total_price']:.2f}) from {item['store_name']}")
        
        return "\n".join(response_parts)
    
    def _format_spending_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format spending total response."""
        if not results:
            return "I couldn't find any spending information for your query."
        
        result = results[0]
        total = result['total_spending']
        
        if result['type'] == 'daily_total':
            date_str = result['date'].strftime('%B %d, %Y')
            return f"Your total food expenses on {date_str} were ${total:.2f}."
        
        elif result['type'] == 'range_total':
            start_str = result['start_date'].strftime('%B %d, %Y')
            end_str = result['end_date'].strftime('%B %d, %Y')
            return f"Your total food expenses from {start_str} to {end_str} were ${total:.2f}."
        
        elif result['type'] == 'days_back_total':
            days = result['days_back']
            return f"Your total food expenses over the last {days} days were ${total:.2f}."
        
        return f"Your total food expenses were ${total:.2f}."
    
    def _format_semantic_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format semantic search response."""
        if len(results) == 0:
            return "I couldn't find any similar items matching your search."
        
        # Group items by similarity score ranges
        high_similarity = [r for r in results if r.get('similarity_score', 0) > 0.5]
        medium_similarity = [r for r in results if 0.3 < r.get('similarity_score', 0) <= 0.5]
        
        response_parts = []
        
        if high_similarity:
            response_parts.append(f"Found {len(high_similarity)} highly similar items:")
            for item in high_similarity:
                similarity = item.get('similarity_score', 0)
                response_parts.append(f"• {item['item_name']} (similarity: {similarity:.1%}) - ${item['total_price']:.2f} from {item['store_name']}")
        
        if medium_similarity:
            if high_similarity:
                response_parts.append(f"\nAlso found {len(medium_similarity)} moderately similar items:")
            else:
                response_parts.append(f"Found {len(medium_similarity)} similar items:")
            
            for item in medium_similarity[:3]:  # Limit to top 3
                similarity = item.get('similarity_score', 0)
                response_parts.append(f"• {item['item_name']} (similarity: {similarity:.1%}) - ${item['total_price']:.2f} from {item['store_name']}")
        
        return "\n".join(response_parts)
    
    def _format_stores_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format stores list response."""
        if not results:
            return "I couldn't find any store information for your query."
        
        result = results[0]
        stores = result['stores']
        item_name = result['item_name']
        days_back = result.get('days_back')
        
        if not stores:
            time_phrase = f"in the last {days_back} days" if days_back else "in your receipts"
            return f"I couldn't find any stores where you bought {item_name} {time_phrase}."
        
        time_phrase = f"in the last {days_back} days" if days_back else ""
        
        if len(stores) == 1:
            return f"You bought {item_name} from {stores[0]} {time_phrase}."
        else:
            stores_list = ", ".join(stores[:-1]) + f", and {stores[-1]}"
            return f"You bought {item_name} from {stores_list} {time_phrase}."
    
    def _format_general_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format general response using AI."""
        try:
            # Use AI to format the response naturally
            system_prompt = """You are a helpful assistant that formats database query results into natural language responses about food receipts and purchases. 
            Be conversational, helpful, and concise. Focus on the key information the user is asking about."""
            
            user_prompt = f"""
            User query: "{query}"
            Database results: {json.dumps(results, default=str, indent=2)}
            
            Please format this into a natural, helpful response for the user.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat_completion(messages, max_tokens=300)
            return response['choices'][0]['message']['content'].strip()
        
        except Exception as e:
            # Fallback to simple formatting
            return f"I found {len(results)} results for your query, but had trouble formatting the response. Please try rephrasing your question."
    
    def _format_no_results_response(self, query: str, parsed_query: Dict[str, Any]) -> str:
        """Format response when no results are found."""
        intent = parsed_query['intent']
        
        if intent == 'list_items':
            return "I couldn't find any food items matching your query. Try asking about a different time period or check if you have uploaded receipts for that date."
        elif intent == 'total_spending':
            return "I couldn't find any spending information for the specified time period. Make sure you have uploaded receipts for those dates."
        elif intent == 'find_stores':
            return "I couldn't find any stores matching your query. Try asking about a different item or time period."
        else:
            return "I couldn't find any information matching your query. Please try rephrasing your question or check if you have uploaded relevant receipts."


class AIQueryService:
    """Main service class for processing natural language queries about receipts."""
    
    def __init__(self):
        """Initialize the AI query service."""
        if not config.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is required for AI query functionality")
        
        self.openrouter_client = OpenRouterClient(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.OPENROUTER_MODEL
        )
        self.query_parser = QueryParser()
        self.sql_generator = SQLQueryGenerator(db_service)
        self.response_formatter = ResponseFormatter(self.openrouter_client)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return a formatted response.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing the response and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Parse the query
            parsed_query = self.query_parser.parse_query(query)
            
            # Generate database results
            results = self.sql_generator.generate_query_results(parsed_query)
            
            # Format the response
            formatted_response = self.response_formatter.format_response(
                query, results, parsed_query
            )
            
            execution_time = time.time() - start_time
            
            return {
                'query': query,
                'parsed_query': parsed_query,
                'results': results,
                'formatted_response': formatted_response,
                'execution_time': execution_time,
                'success': True
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                'query': query,
                'error': str(e),
                'formatted_response': f"I'm sorry, I encountered an error processing your query: {str(e)}",
                'execution_time': execution_time,
                'success': False
            }
    
    def get_query_suggestions(self) -> List[str]:
        """Get example queries that users can try."""
        return [
            "What food did I buy yesterday?",
            "Give me total expenses for food on 20 June",
            "Where did I buy hamburger from last 7 days?",
            "Show me all items I bought this week",
            "How much did I spend on food last month?",
            "What stores did I shop at yesterday?",
            "List all pizza purchases from the last 30 days"
        ]


# Global AI query service instance
ai_query_service = None

def get_ai_query_service() -> Optional[AIQueryService]:
    """Get the global AI query service instance."""
    global ai_query_service
    
    if ai_query_service is None:
        try:
            ai_query_service = AIQueryService()
        except ValueError as e:
            print(f"Warning: {e}")
            return None
    
    return ai_query_service