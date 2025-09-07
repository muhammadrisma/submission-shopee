"""
Unit tests for AI Query Service.
Tests query parsing, SQL generation, response formatting, and integration.
"""

import json
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

from models.receipt import Receipt, ReceiptItem
from services.ai_query import (
    AIQueryService,
    OpenRouterClient,
    QueryParser,
    ResponseFormatter,
    SQLQueryGenerator,
    get_ai_query_service,
)


class TestOpenRouterClient(unittest.TestCase):
    """Test OpenRouter API client."""

    def setUp(self):
        """Set up test client."""
        self.client = OpenRouterClient(
            api_key="test_key", base_url="https://test.api.com", model="test/model"
        )

    def test_client_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, "test_key")
        self.assertEqual(self.client.base_url, "https://test.api.com")
        self.assertEqual(self.client.model, "test/model")
        self.assertIn("Authorization", self.client.headers)

    @patch("requests.post")
    def test_chat_completion_success(self, mock_post):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "Test message"}]
        result = self.client.chat_completion(messages)

        self.assertEqual(result["choices"][0]["message"]["content"], "Test response")
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_chat_completion_request_error(self, mock_post):
        """Test chat completion with request error."""
        mock_post.side_effect = Exception("Network error")

        messages = [{"role": "user", "content": "Test message"}]

        with self.assertRaises(Exception) as context:
            self.client.chat_completion(messages)

        self.assertIn("OpenRouter API request failed", str(context.exception))


class TestQueryParser(unittest.TestCase):
    """Test natural language query parser."""

    def setUp(self):
        """Set up test parser."""
        self.parser = QueryParser()

    def test_parse_item_query_yesterday(self):
        """Test parsing item query for yesterday."""
        query = "What food did I buy yesterday?"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "list_items")
        self.assertEqual(
            result["parameters"]["specific_date"], date.today() - timedelta(days=1)
        )
        self.assertGreater(result["confidence"], 0.7)

    def test_parse_spending_query_specific_date(self):
        """Test parsing spending query for specific date."""
        query = "Give me total expenses for food on 20 June"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "total_spending")
        expected_date = date(date.today().year, 6, 20)
        self.assertEqual(result["parameters"]["specific_date"], expected_date)
        self.assertGreater(result["confidence"], 0.8)

    def test_parse_store_query_with_item(self):
        """Test parsing store query with item name."""
        query = "Where did I buy hamburger from last 7 days?"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "find_stores")
        self.assertEqual(result["parameters"]["item_name"], "hamburger")
        self.assertEqual(result["parameters"]["days_back"], 7)
        self.assertGreater(result["confidence"], 0.7)

    def test_parse_query_last_week(self):
        """Test parsing query with 'last week' time reference."""
        query = "What did I buy last week?"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "list_items")
        self.assertIsNotNone(result["parameters"]["date_range"])
        self.assertIsInstance(result["parameters"]["date_range"], tuple)

    def test_parse_query_days_back(self):
        """Test parsing query with 'last X days' pattern."""
        query = "Show me items from last 30 days"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "list_items")
        self.assertEqual(result["parameters"]["days_back"], 30)

    def test_parse_general_query(self):
        """Test parsing general/unknown query."""
        query = "Random question about something"
        result = self.parser.parse_query(query)

        self.assertEqual(result["intent"], "general")
        self.assertLess(result["confidence"], 0.5)

    def test_extract_item_name(self):
        """Test item name extraction."""
        test_cases = [
            ("I bought pizza yesterday", "pizza"),
            ("Did I buy hamburger?", "hamburger"),
            ("Show me purchases of coffee", "coffee"),
            ("Where did I get bread?", "bread"),
        ]

        for query, expected_item in test_cases:
            item = self.parser._extract_item_name(query)
            self.assertEqual(item, expected_item)

    def test_get_week_range(self):
        """Test week range calculation."""
        start, end = self.parser._get_week_range()

        self.assertEqual(start.weekday(), 0)
        self.assertEqual(end.weekday(), 6)
        self.assertEqual((end - start).days, 6)

    def test_get_month_range(self):
        """Test month range calculation."""
        start, end = self.parser._get_month_range()

        today = date.today()
        self.assertEqual(start.day, 1)
        self.assertEqual(start.month, today.month)
        self.assertEqual(start.year, today.year)


class TestSQLQueryGenerator(unittest.TestCase):
    """Test SQL query generator."""

    def setUp(self):
        """Set up test generator with mock database service."""
        self.mock_db_service = Mock()
        self.generator = SQLQueryGenerator(self.mock_db_service)

    def test_query_items_specific_date(self):
        """Test querying items for specific date."""
        mock_item = ReceiptItem(
            id=1,
            receipt_id=1,
            item_name="Pizza",
            quantity=1,
            unit_price=Decimal("12.99"),
            total_price=Decimal("12.99"),
        )
        mock_receipt = Receipt(
            id=1,
            store_name="Pizza Place",
            receipt_date=date.today(),
            total_amount=Decimal("12.99"),
            upload_timestamp=datetime.now(),
            raw_text="",
            image_path="",
            items=[mock_item],
        )

        self.mock_db_service.get_receipts_by_date_range.return_value = [mock_receipt]

        parsed_query = {
            "intent": "list_items",
            "parameters": {"specific_date": date.today()},
        }

        results = self.generator.generate_query_results(parsed_query)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["item_name"], "Pizza")
        self.assertEqual(results[0]["store_name"], "Pizza Place")
        self.mock_db_service.get_receipts_by_date_range.assert_called_once()

    def test_query_spending_date_range(self):
        """Test querying spending for date range."""
        mock_receipts = [
            Receipt(
                id=1,
                store_name="Store A",
                receipt_date=date.today(),
                total_amount=Decimal("25.50"),
                upload_timestamp=datetime.now(),
                raw_text="",
                image_path="",
                items=[],
            ),
            Receipt(
                id=2,
                store_name="Store B",
                receipt_date=date.today(),
                total_amount=Decimal("15.75"),
                upload_timestamp=datetime.now(),
                raw_text="",
                image_path="",
                items=[],
            ),
        ]

        self.mock_db_service.get_receipts_by_date_range.return_value = mock_receipts

        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

        parsed_query = {
            "intent": "total_spending",
            "parameters": {"date_range": (start_date, end_date)},
        }

        results = self.generator.generate_query_results(parsed_query)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["total_spending"], Decimal("41.25"))
        self.assertEqual(results[0]["type"], "range_total")

    def test_query_stores_with_item(self):
        """Test querying stores that sold specific item."""
        self.mock_db_service.get_stores_with_item.return_value = ["Store A", "Store B"]

        parsed_query = {
            "intent": "find_stores",
            "parameters": {"item_name": "hamburger", "days_back": 7},
        }

        results = self.generator.generate_query_results(parsed_query)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["stores"], ["Store A", "Store B"])
        self.assertEqual(results[0]["item_name"], "hamburger")
        self.mock_db_service.get_stores_with_item.assert_called_once_with(
            "hamburger", 7
        )

    def test_query_unknown_intent(self):
        """Test querying with unknown intent."""
        parsed_query = {"intent": "unknown", "parameters": {}}

        results = self.generator.generate_query_results(parsed_query)

        self.assertEqual(len(results), 0)


class TestResponseFormatter(unittest.TestCase):
    """Test response formatter."""

    def setUp(self):
        """Set up test formatter with mock OpenRouter client."""
        self.mock_client = Mock()
        self.formatter = ResponseFormatter(self.mock_client)

    def test_format_items_response_single_date(self):
        """Test formatting items response for single date."""
        results = [
            {
                "item_name": "Pizza",
                "quantity": 1,
                "total_price": Decimal("12.99"),
                "store_name": "Pizza Place",
                "receipt_date": date.today(),
            },
            {
                "item_name": "Soda",
                "quantity": 2,
                "total_price": Decimal("3.50"),
                "store_name": "Pizza Place",
                "receipt_date": date.today(),
            },
        ]

        parsed_query = {"intent": "list_items"}
        response = self.formatter.format_response(
            "What did I buy today?", results, parsed_query
        )

        self.assertIn("Pizza", response)
        self.assertIn("Soda", response)
        self.assertIn("Pizza Place", response)
        self.assertIn("$12.99", response)
        self.assertIn("$3.50", response)

    def test_format_spending_response_daily(self):
        """Test formatting spending response for daily total."""
        results = [
            {
                "total_spending": Decimal("25.49"),
                "date": date.today(),
                "type": "daily_total",
            }
        ]

        parsed_query = {"intent": "total_spending"}
        response = self.formatter.format_response(
            "How much did I spend today?", results, parsed_query
        )

        self.assertIn("$25.49", response)
        self.assertIn(date.today().strftime("%B %d, %Y"), response)

    def test_format_stores_response_multiple(self):
        """Test formatting stores response with multiple stores."""
        results = [
            {
                "stores": ["Store A", "Store B", "Store C"],
                "item_name": "hamburger",
                "days_back": 7,
                "type": "stores_with_item",
            }
        ]

        parsed_query = {"intent": "find_stores"}
        response = self.formatter.format_response(
            "Where did I buy hamburger?", results, parsed_query
        )

        self.assertIn("hamburger", response)
        self.assertIn("Store A", response)
        self.assertIn("Store B", response)
        self.assertIn("Store C", response)

    def test_format_no_results_response(self):
        """Test formatting response when no results found."""
        parsed_query = {"intent": "list_items"}
        response = self.formatter.format_response("What did I buy?", [], parsed_query)

        self.assertIn("couldn't find", response.lower())

    @patch.object(ResponseFormatter, "_format_general_response")
    def test_format_general_response_with_ai(self, mock_general):
        """Test formatting general response using AI."""
        mock_general.return_value = "AI formatted response"

        results = [{"some": "data"}]
        parsed_query = {"intent": "general"}

        response = self.formatter.format_response(
            "General query", results, parsed_query
        )

        mock_general.assert_called_once()


class TestAIQueryService(unittest.TestCase):
    """Test main AI query service."""

    @patch("services.ai_query.config")
    def setUp(self, mock_config):
        """Set up test service with mocked dependencies."""
        mock_config.OPENROUTER_API_KEY = "test_key"
        mock_config.OPENROUTER_BASE_URL = "https://test.api.com"
        mock_config.OPENROUTER_MODEL = "test/model"

        with (
            patch("services.ai_query.OpenRouterClient"),
            patch("services.ai_query.db_service"),
        ):
            self.service = AIQueryService()

    @patch("services.ai_query.config")
    def test_service_initialization_no_api_key(self, mock_config):
        """Test service initialization without API key."""
        mock_config.OPENROUTER_API_KEY = None

        with self.assertRaises(ValueError) as context:
            AIQueryService()

        self.assertIn("OpenRouter API key is required", str(context.exception))

    def test_process_query_success(self):
        """Test successful query processing."""
        self.service.query_parser = Mock()
        self.service.sql_generator = Mock()
        self.service.response_formatter = Mock()

        parsed_query = {"intent": "list_items", "parameters": {}}
        results = [{"item": "test"}]
        formatted_response = "Test response"

        self.service.query_parser.parse_query.return_value = parsed_query
        self.service.sql_generator.generate_query_results.return_value = results
        self.service.response_formatter.format_response.return_value = (
            formatted_response
        )

        result = self.service.process_query("Test query")

        self.assertTrue(result["success"])
        self.assertEqual(result["query"], "Test query")
        self.assertEqual(result["parsed_query"], parsed_query)
        self.assertEqual(result["results"], results)
        self.assertEqual(result["formatted_response"], formatted_response)
        self.assertGreaterEqual(result["execution_time"], 0)

    def test_process_query_error(self):
        """Test query processing with error."""
        self.service.query_parser = Mock()
        self.service.query_parser.parse_query.side_effect = Exception("Test error")

        result = self.service.process_query("Test query")

        self.assertFalse(result["success"])
        self.assertEqual(result["query"], "Test query")
        self.assertIn("Test error", result["error"])
        self.assertIn("error processing", result["formatted_response"])
        self.assertGreaterEqual(result["execution_time"], 0)

    def test_get_query_suggestions(self):
        """Test getting query suggestions."""
        suggestions = self.service.get_query_suggestions()

        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(all(isinstance(s, str) for s in suggestions))


class TestGlobalServiceInstance(unittest.TestCase):
    """Test global service instance management."""

    def setUp(self):
        """Reset global service instance."""
        import services.ai_query

        services.ai_query.ai_query_service = None

    @patch("services.ai_query.config")
    @patch("services.ai_query.AIQueryService")
    def test_get_ai_query_service_success(self, mock_service_class, mock_config):
        """Test getting AI query service successfully."""
        mock_config.OPENROUTER_API_KEY = "test_key"
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance

        service = get_ai_query_service()

        self.assertEqual(service, mock_service_instance)
        mock_service_class.assert_called_once()

    @patch("services.ai_query.config")
    @patch("services.ai_query.AIQueryService")
    def test_get_ai_query_service_no_api_key(self, mock_service_class, mock_config):
        """Test getting AI query service without API key."""
        mock_config.OPENROUTER_API_KEY = None
        mock_service_class.side_effect = ValueError("API key required")

        service = get_ai_query_service()

        self.assertIsNone(service)

    @patch("services.ai_query.config")
    @patch("services.ai_query.AIQueryService")
    def test_get_ai_query_service_singleton(self, mock_service_class, mock_config):
        """Test that service instance is singleton."""
        mock_config.OPENROUTER_API_KEY = "test_key"
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance

        service1 = get_ai_query_service()
        service2 = get_ai_query_service()

        self.assertEqual(service1, service2)
        mock_service_class.assert_called_once()


if __name__ == "__main__":
    unittest.main()
