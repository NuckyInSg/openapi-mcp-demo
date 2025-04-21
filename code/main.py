from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("openapi")

# Constants
API_BASE_URL = "https://18.143.168.167:49900"
USER_AGENT = "openapi-mcp/1.0"

# 创建一个全局的 HTTP 客户端
async def get_client() -> httpx.AsyncClient:
    """获取一个配置好的 HTTP 客户端实例"""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=30.0,
        verify=False,  # 忽略 SSL 证书验证
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        }
    )

async def make_api_request(
    method: str,
    url: str,
    token: str = None,
    **kwargs
) -> Dict[str, Any] | None:
    """发送 API 请求并处理错误"""
    async with await get_client() as client:
        try:
            headers = kwargs.pop("headers", {})
            if token:
                # 直接使用 token 而不添加 Bearer 前缀
                headers["Authorization"] = token
            
            response = await client.request(
                method,
                url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": 500,
                "action": "alert",
                "message": str(e),
                "data": None,
                "success": False
            }

@mcp.tool()
async def issue_token(access_key_id: str, access_key_secret: str) -> Dict[str, Any]:
    """获取 OpenAPI 访问令牌
    
    Args:
        access_key_id: OpenAPI 访问密钥 ID
        access_key_secret: OpenAPI 访问密钥密文
    
    Returns:
        Dict 包含 access_token 和 expires_in 的字典
    """
    request_data = {
        "access_key_id": access_key_id,
        "access_key_secret": access_key_secret
    }
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/token",
        json=request_data
    )
    
    if not result or "error" in result:
        return {
            "success": False,
            "error": result.get("error", "Failed to get token")
        }
    
    data = result.get("data", {})
    return {
        "success": True,
        "data": {
            "access_token": data.get("access_token"),
            "expires_in": data.get("expires_in")
        }
    }



# 部门相关接口
@mcp.tool()
async def department_list(token: str, department_id: Optional[str] = None) -> Dict[str, Any]:
    """获取部门列表
    
    Args:
        token: OpenAPI 访问令牌
        department_id: 可选，部门ID，不传则获取根部门
    
    Returns:
        Dict 包含部门列表信息
    """
    params = {}
    if department_id:
        params["id"] = department_id
    
    result = await make_api_request(
        "GET",
        "/api/open/v1/department/list",
        token=token,
        params=params
    )
    
    return result

@mcp.tool()
async def department_detail(token: str, department_id: str) -> Dict[str, Any]:
    """获取单个部门详情
    
    Args:
        token: OpenAPI 访问令牌
        department_id: 部门ID
    
    Returns:
        Dict 包含部门详细信息
    """
    params = {"param": department_id}
    
    result = await make_api_request(
        "GET",
        "/api/open/v1/department/detail",
        token=token,
        params=params
    )
    
    return result

@mcp.tool()
async def department_create(token: str, name: str, parent_id: str, order: Optional[int] = None) -> Dict[str, Any]:
    """创建单个部门
    
    Args:
        token: OpenAPI 访问令牌
        name: 部门名称
        parent_id: 父部门ID
        order: 可选，排序值
    
    Returns:
        Dict 包含创建结果
    """
    request_data = {
        "name": name,
        "parent_id": parent_id
    }
    
    if order is not None:
        request_data["order"] = order
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/department/create",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def department_update(token: str, department_id: str, name: Optional[str] = None, order: Optional[int] = None) -> Dict[str, Any]:
    """更新部门信息
    
    Args:
        token: OpenAPI 访问令牌
        department_id: 部门ID
        name: 可选，部门名称
        order: 可选，排序值
    
    Returns:
        Dict 包含更新结果
    """
    request_data = {"id": department_id}
    
    if name is not None:
        request_data["name"] = name
    
    if order is not None:
        request_data["order"] = order
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/department/update",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def department_delete(token: str, department_id: str) -> Dict[str, Any]:
    """删除部门
    
    Args:
        token: OpenAPI 访问令牌
        department_id: 部门ID
    
    Returns:
        Dict 包含删除结果
    """
    request_data = {"id": department_id}
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/department/delete",
        token=token,
        json=request_data
    )
    
    return result

# 角色相关接口
@mcp.tool()
async def role_list(token: str) -> Dict[str, Any]:
    """获取角色列表
    
    Args:
        token: OpenAPI 访问令牌
    
    Returns:
        Dict 包含角色列表信息
    """
    result = await make_api_request(
        "GET",
        "/api/open/v1/role/list",
        token=token
    )
    
    return result

@mcp.tool()
async def role_get(token: str, role_id: str) -> Dict[str, Any]:
    """获取角色详情
    
    Args:
        token: OpenAPI 访问令牌
        role_id: 角色ID
    
    Returns:
        Dict 包含角色详细信息
    """
    params = {"id": role_id}
    
    result = await make_api_request(
        "GET",
        "/api/open/v1/role/get",
        token=token,
        params=params
    )
    
    return result

@mcp.tool()
async def role_create(token: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """创建角色
    
    Args:
        token: OpenAPI 访问令牌
        name: 角色名称
        description: 可选，角色描述
    
    Returns:
        Dict 包含创建结果
    """
    request_data = {"name": name}
    
    if description is not None:
        request_data["description"] = description
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/role/create",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def role_update(token: str, role_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """更新角色基本信息
    
    Args:
        token: OpenAPI 访问令牌
        role_id: 角色ID
        name: 可选，角色名称
        description: 可选，角色描述
    
    Returns:
        Dict 包含更新结果
    """
    request_data = {"id": role_id}
    
    if name is not None:
        request_data["name"] = name
    
    if description is not None:
        request_data["description"] = description
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/role/update",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def role_delete(token: str, role_id: str) -> Dict[str, Any]:
    """删除角色
    
    Args:
        token: OpenAPI 访问令牌
        role_id: 角色ID
    
    Returns:
        Dict 包含删除结果
    """
    request_data = {"id": role_id}
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/role/delete",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def role_member_create(token: str, role_id: str, user_ids: List[str]) -> Dict[str, Any]:
    """添加角色成员
    
    Args:
        token: OpenAPI 访问令牌
        role_id: 角色ID
        user_ids: 用户ID列表
    
    Returns:
        Dict 包含添加结果
    """
    request_data = {
        "role_id": role_id,
        "user_ids": user_ids
    }
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/role/member/create",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def role_member_delete(token: str, role_id: str, user_ids: List[str]) -> Dict[str, Any]:
    """删除角色成员
    
    Args:
        token: OpenAPI 访问令牌
        role_id: 角色ID
        user_ids: 用户ID列表
    
    Returns:
        Dict 包含删除结果
    """
    request_data = {
        "role_id": role_id,
        "user_ids": user_ids
    }
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/role/member/delete",
        token=token,
        json=request_data
    )
    
    return result

# 用户相关接口
@mcp.tool()
async def user_list(token: str, department_id: str, recursive: Optional[bool] = None) -> Dict[str, Any]:
    """获取部门成员
    
    Args:
        token: OpenAPI 访问令牌
        department_id: 部门ID
        recursive: 可选，是否递归获取子部门成员
    
    Returns:
        Dict 包含用户列表信息
    """
    params = {"department_id": department_id}
    
    if recursive is not None:
        params["recursive"] = 1 if recursive else 0
    
    result = await make_api_request(
        "GET",
        "/api/open/v1/user/list",
        token=token,
        params=params
    )
    
    return result

@mcp.tool()
async def user_get(token: str, user_id: str) -> Dict[str, Any]:
    """获取用户详情
    
    Args:
        token: OpenAPI 访问令牌
        user_id: 用户ID
    
    Returns:
        Dict 包含用户详细信息
    """
    params = {"id": user_id}
    
    result = await make_api_request(
        "GET",
        "/api/open/v1/user/get",
        token=token,
        params=params
    )
    
    return result

@mcp.tool()
async def user_create(token: str, username: str, full_name: str, department_id: str, email: Optional[str] = None, 
                      mobile: Optional[str] = None, password: Optional[str] = None, gender: int = 1, status: int = 1) -> Dict[str, Any]:
    """添加单个用户
    
    Args:
        token: OpenAPI 访问令牌
        username: 用户名
        full_name: 姓名
        department_id: 部门ID
        email: 可选，邮箱
        mobile: 可选，手机号
        password: 可选，密码
        gender: 可选，性别，1男、2女，默认1
        status: 可选，状态，1正常，2禁用，默认1
    
    Returns:
        Dict 包含创建结果
    """
    request_data = {
        "username": username,
        "full_name": full_name,
        "department_id": department_id,
        "gender": gender,
        "status": status
    }
    
    if email is not None:
        request_data["email"] = email
    
    if mobile is not None:
        request_data["mobile"] = mobile
    
    if password is not None:
        request_data["password"] = password
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/user/create",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def user_set_status(token: str, user_id: str, status: int) -> Dict[str, Any]:
    """设置用户状态
    
    Args:
        token: OpenAPI 访问令牌
        user_id: 用户ID
        status: 状态（1=正常，2=禁用，3=离职，4=未激活）
    
    Returns:
        Dict 包含设置结果
    """
    # 使用 user_update API 来设置用户状态
    return await user_update(token, user_id, status=status)

@mcp.tool()
async def user_update(token: str, user_id: str, full_name: Optional[str] = None, email: Optional[str] = None, 
                      mobile: Optional[str] = None, department_id: Optional[str] = None, role_ids: Optional[List[str]] = None,
                      status: Optional[int] = None) -> Dict[str, Any]:
    """更新用户信息
    
    Args:
        token: OpenAPI 访问令牌
        user_id: 用户ID
        full_name: 可选，姓名
        email: 可选，邮箱
        mobile: 可选，手机号
        department_id: 可选，部门ID
        role_ids: 可选，角色ID列表
        status: 可选，用户状态（1=正常，2=禁用，3=离职，4=未激活）
    
    Returns:
        Dict 包含更新结果
    """
    request_data = {"id": user_id}
    
    if full_name is not None:
        request_data["full_name"] = full_name
    
    if email is not None:
        request_data["email"] = email
    
    if mobile is not None:
        request_data["mobile"] = mobile
    
    if department_id is not None:
        request_data["department_id"] = department_id
    
    if role_ids is not None:
        request_data["role_ids"] = role_ids
        
    if status is not None:
        request_data["status"] = status
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/user/update",
        token=token,
        json=request_data
    )
    
    return result

@mcp.tool()
async def user_delete(token: str, user_id: str, set_offline_first: bool = True) -> Dict[str, Any]:
    """删除用户
    
    Args:
        token: OpenAPI 访问令牌
        user_id: 用户ID
        set_offline_first: 是否先将用户设置为离职状态，默认为 True
    
    Returns:
        Dict 包含删除结果
    """
    # 如果需要，先将用户设置为离职状态
    if set_offline_first:
        # 离职状态为 3
        status_result = await user_update(token, user_id, status=3)
        if status_result.get("code") != 0:
            return {
                "code": status_result.get("code", 500),
                "action": "alert",
                "message": f"设置用户为离职状态失败: {status_result.get('message', '')}",
                "data": None
            }
    
    # 删除用户
    request_data = {"id": user_id}
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/user/delete",
        token=token,
        json=request_data
    )
    
    # 如果失败，添加提示信息
    if result.get("code") != 0:
        result["message"] = f"{result.get('message', '')}。注意: 只能删除离职用户，可能需要等待一段时间才能删除。"
    
    return result

@mcp.tool()
async def user_batch_get_id(token: str, usernames: List[str]) -> Dict[str, Any]:
    """批量获取用户的 open id
    
    Args:
        token: OpenAPI 访问令牌
        usernames: 用户名列表
    
    Returns:
        Dict 包含用户ID信息
    """
    request_data = {"usernames": usernames}
    
    result = await make_api_request(
        "POST",
        "/api/open/v1/user/batch_get_id",
        token=token,
        json=request_data
    )
    
    return result

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')