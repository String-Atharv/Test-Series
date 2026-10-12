from httpx import AsyncClient

#Test 1 : Successful Registration
async def test_register_user(async_client:AsyncClient):
    payload={
        "username":"atharv shivale",
        "email":"atharv@gmail.com",
        "password":"123",
        "role":"student"
    }

    # send request
    response=await async_client.post("/api/v1/users/register", json=payload)

    # Assert response status and data matches what we expect
    assert response.status_code==201
    data=response.json()
    assert data["username"]==payload["username"]
    assert data["email"]==payload["email"]
    assert "id" in data
    assert "password" not in data

#Test 2 : cannot register with already registered user
async def test_register_duplicate_user(async_client:AsyncClient):
    payload={
        "username":"atharv shivale",
        "email":"atharv@gmail.com",
        "password":"123",
        "role":"student"
    }

    # first registration
    res1=await async_client.post("/api/v1/users/register",json=payload)
    assert res1.status_code==201

    # second registration
    res2=await async_client.post("/api/v1/users/register",json=payload)

    # second registration should fail
    assert res2.status_code in [400,409]


# Test 3 : successfull user authentication
async def test_successful_authentication(async_client:AsyncClient):
    # register first
    payload={
        "username":"atharv",
        "email":"atharv@gmail.com",
        "password":"23",
        "role":"student"
    }
    await async_client.post("/api/v1/users/register",json=payload)

    #now authenticate
    payload2={
        "email":"atharv@gmail.com",
        "password":"23"
    }

    res=await async_client.post("/api/v1/users/authenticate",json=payload2)
    assert res.status_code==200
    data=res.json()
    assert "access_token" in data
    assert data["token_type"]=="bearer"

# Test 4: User not registered returns 404
async def test_authentication_user_not_found(async_client: AsyncClient):
    payload = {
        "email": "nonexistent@gmail.com",
        "password": "23"
    }
    res = await async_client.post("/api/v1/users/authenticate", json=payload)
    assert res.status_code == 404
    assert res.json()["detail"] == "user not registered"


# Test 5: Wrong password returns 401
async def test_authentication_wrong_password(async_client: AsyncClient):
    # 1. Register user
    reg_payload = {
        "username": "atharv",
        "email": "atharv@gmail.com",
        "password": "23",
        "role": "student"
    }
    await async_client.post("/api/v1/users/register", json=reg_payload)

    # 2. Login with correct email, wrong password
    login_payload = {
        "email": "atharv@gmail.com",
        "password": "wrongpassword"
    }
    res = await async_client.post("/api/v1/users/authenticate", json=login_payload)
    assert res.status_code == 401
    assert res.json()["detail"] == "invalid credentials"

# Test 6 : Acesssing endpoint using jwt token
async def test_protected_route(async_client:AsyncClient):
    # register first
    payload={
        "username":"atharv",
        "email":"atharv@gmail.com",
        "password":"23",
        "role":"student"
    }
    await async_client.post("/api/v1/users/register",json=payload)

    #now authenticate
    payload2={
        "email":"atharv@gmail.com",
        "password":"23"
    }

    login_res = await async_client.post("/api/v1/users/authenticate", json=payload2)
    token = login_res.json()["access_token"]

    # 3. Request protected route using GET with Bearer token header
    headers = {"Authorization": f"Bearer {token}"}
    res = await async_client.get("/api/v1/users/me", headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    


    

   


