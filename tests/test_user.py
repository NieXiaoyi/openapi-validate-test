import pytest

from openapi_core import Spec
from openapi_core.validation.request import V30RequestValidator
from openapi_core.validation.response import V30ResponseValidator
from openapi_core.exceptions import OpenAPIError
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse
from requests import Request, Response


base_api_url = 'http://localhost:8000/api'
openapi_spec = Spec.from_file_path('openapi/user.yml')
request_validator = V30RequestValidator(openapi_spec)
response_validator = V30ResponseValidator(openapi_spec)


class TestAuth:
    def test_auth_success(self):
        """Test successful authentication"""
        url = f'{base_api_url}/auth'
        request = Request('POST', url, json={'username': 'testuser', 'password': 'testpass'})
        openapi_request = RequestsOpenAPIRequest(request)
        request_validator.validate(openapi_request)
        # 验证响应
        response = Response()
        response.status_code = 200
        response.headers = {"Content-Type": "application/json", "X-Auth-Token": "testtoken"}
        response._content = b'{"message": "Authentication successful"}'
        openapi_response = RequestsOpenAPIResponse(response)
        response_validator.validate(openapi_request, openapi_response)


class TestListUsers:
    def test_list_users_success(self):
        """Test successful retrieval of user list"""
        url = f'{base_api_url}/users'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)
        request_validator.validate(openapi_request)
        # 验证响应
        response = Response()
        response.status_code = 200
        response._content = b'[{"id": "123e4567-e89b-12d3-a456-426614174000", "username": "Test User", "age": 30}]'
        response.headers = {'Content-Type': 'application/json'}
        openapi_response = RequestsOpenAPIResponse(response)
        response_validator.validate(openapi_request, openapi_response)

class TestGetUser:
    def test_valid_uuid_format(self):
        """Test validation of a valid GET user response"""
        url = f'{base_api_url}/users/123e4567-e89b-12d3-a456-426614174000'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)
        request_validator.validate(openapi_request)
        
        response = Response()
        response.status_code = 200
        response._content = b'{"id": "123e4567-e89b-12d3-a456-426614174000", "username": "Test User", "age": 30}'
        response.headers = {'Content-Type': 'application/json'}
        openapi_response = RequestsOpenAPIResponse(response)
        response_validator.validate(openapi_request, openapi_response)
    
    def test_invalid_uuid_format(self):
        """Test validation fails with invalid UUID format and returns error response"""
        url = f'{base_api_url}/users/invalid-uuid'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)

        # Validate request should fail
        with pytest.raises(OpenAPIError):
            request_validator.validate(openapi_request)

        response = Response()
        response.status_code = 400
        response._content = b'{"code": "USER_0x00001",  "message": "invalid user id"}'
        response.headers = {'Content-Type': 'application/json'}
        openapi_response = RequestsOpenAPIResponse(response)
        
        assert response.status_code  == 400, f"无效UUID请求返回了{response.status_code}状态码，预期应为400"
        # Validate response against OpenAPI spec
        with pytest.raises(OpenAPIError):
            response_validator.validate(openapi_request, openapi_response)
    
    def test_invalid_type_of_age(self):
        """Test validation fails with invalid type of age"""
        url = f'{base_api_url}/users/123e4567-e89b-12d3-a456-426614174000'
        request = Request('GET', url)
        openapi_request = RequestsOpenAPIRequest(request)

        response = Response()
        response.status_code = 200
        # the type of age is string, not integer
        response._content = b'{"id": "123e4567-e89b-12d3-a456-426614174000", "username": "Test User", "age": "30"}'
        response.headers = {'Content-Type': 'application/json'}
        openapi_response = RequestsOpenAPIResponse(response)
        # Validate response against OpenAPI spec
        with pytest.raises(OpenAPIError):
            response_validator.validate(openapi_request, openapi_response)

class TestDeleteUser:
    def test_valid_delete_request(self):
        """Test validation of a valid DELETE user request"""
        url = f'{base_api_url}/users/123e4567-e89b-12d3-a456-426614174000'
        request = Request('DELETE', url)
        openapi_request = RequestsOpenAPIRequest(request)

        request_validator.validate(openapi_request)

    def test_invalid_delete_uuid(self):
        """Test validation fails with invalid UUID for delete request"""
        url = f'{base_api_url}/users/invalid-uuid'
        request = Request('DELETE', url)
        openapi_request = RequestsOpenAPIRequest(request)

        with pytest.raises(OpenAPIError):
            request_validator.validate(openapi_request)
