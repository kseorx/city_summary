import unittest
from unittest.mock import patch
from clients.http import fetch_get, ExternalServiceError
from requests.exceptions import ConnectionError

class TestHttpClientRetry(unittest.TestCase):
    
    @patch('clients.http.requests.get')
    def test_retry_on_connection_error(self, mock_get):
        """Проверяет, что при ConnectionError делается retry, а после исчерпания выбрасывается ExternalServiceError"""
        # Симулируем 3 неудачные попытки (1 первичная + 2 retry)
        mock_get.side_effect = ConnectionError("Network is down")
        
        with self.assertRaises(ExternalServiceError) as context:
            fetch_get("https://api.example.com/test", max_retries=3)
            
        self.assertIn("Внешний сервис недоступен после повторных попыток", str(context.exception))
        # Проверяем, что requests.get был вызван ровно 3 раза
        self.assertEqual(mock_get.call_count, 3)

    @patch('clients.http.requests.get')
    def test_success_after_retry(self, mock_get):
        """Проверяет, что если сервер ответил после 2-й попытки, данные возвращаются"""
        # 1-я попытка: ошибка, 2-я попытка: успех
        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"rate": 95.5}
        
        mock_get.side_effect = [ConnectionError("Temp fail"), mock_response]
        
        result = fetch_get("https://api.example.com/test", max_retries=3)
        
        self.assertEqual(result, {"rate": 95.5})
        self.assertEqual(mock_get.call_count, 2)

if __name__ == "__main__":
    unittest.main()