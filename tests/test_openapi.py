import pytest

from openapi_core import OpenAPI
from openapi_core.exceptions import OpenAPIError
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse
import requests
from requests import Request, Response

openapi_spec = OpenAPI.from_file_path('swagger.yaml')
base_api_url = 'http://localhost:8000/api'


class TestAuth:
    def test_auth_success(self):
        """Test successful authentication"""
        url = f'{base_api_url}/auth'
        request = Request('POST', url, json={'username': 'testuser', 'password': 'testpass'})
        openapi_request = RequestsOpenAPIRequest(request)
        openapi_spec.validate_request(openapi_request)
        # 验证响应
        response = Response()
        response.status_code = 200
        response.headers = {"Content-Type": "application/json", "X-Auth-Token": "testtoken"}
        response._content = b'{"message": "Authentication successful"}'
        openapi_response = RequestsOpenAPIResponse(response)
        openapi_spec.validate_response(openapi_request, openapi_response)


class TestGetUser:
    def test_valid_uuid_format(self):
        """Test validation of a valid GET user response"""
        url = f'{base_api_url}/users/123e4567-e89b-12d3-a456-426614174000'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)
        openapi_spec.validate_request(openapi_request)
        
        response = Response()
        response.status_code = 200
        response._content = b'{"id": "123e4567-e89b-12d3-a456-426614174000", "username": "Test User", "email": "test@example.com"}'
        response.headers = {'Content-Type': 'application/json'}
        openapi_response = RequestsOpenAPIResponse(response)
        openapi_spec.validate_response(openapi_request, openapi_response)
    
    def test_invalid_uuid_format(self):
        """Test validation fails with invalid UUID format and returns error response"""
        url = f'{base_api_url}/users/invalid-uuid'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)

        # Validate request should fail
        with pytest.raises(OpenAPIError):
            openapi_spec.validate_request(openapi_request)

        # Send actual request and verify response
        session = requests.Session()
        response = session.send(request.prepare())
        openapi_response = RequestsOpenAPIResponse(response)

        # Verify response status code - should not be 200
        assert response.status_code != 200, f"无效UUID请求返回了200状态码，预期应为400或404"
        assert response.status_code in [400, 404], f"无效UUID请求返回了{response.status_code}状态码，预期应为400或404"

        # Validate response against OpenAPI spec
        with pytest.raises(OpenAPIError):
            openapi_spec.validate_response(openapi_request, openapi_response)
        

class TestDeleteUser:
    def test_valid_delete_request(self):
        """Test validation of a valid DELETE user request"""
        url = f'{base_api_url}/users/123e4567-e89b-12d3-a456-426614174000'
        request = Request('DELETE', url)
        openapi_request = RequestsOpenAPIRequest(request)

        openapi_spec.validate_request(openapi_request)

    def test_invalid_delete_uuid(self):
        """Test validation fails with invalid UUID for delete request"""
        url = f'{base_api_url}/users/invalid-uuid'
        request = Request('DELETE', url)
        openapi_request = RequestsOpenAPIRequest(request)

        with pytest.raises(OpenAPIError):
            openapi_spec.validate_request(openapi_request)
