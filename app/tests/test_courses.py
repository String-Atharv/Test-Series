import uuid
from httpx import AsyncClient


# Test 1: Successfully create a course (201 Created)
async def test_create_course(async_client: AsyncClient):
    payload = {
        "name": "CA Foundation",
        "display_order": 1,
    }
    response = await async_client.post("/api/v1/courses/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "CA Foundation"
    assert data["display_order"] == 1
    assert "id" in data
    assert "created_at" in data


# Test 2: Prevent duplicate course name (400 Bad Request)
async def test_create_duplicate_course_name(async_client: AsyncClient):
    payload = {
        "name": "CA Intermediate",
        "display_order": 1,
    }
    res1 = await async_client.post("/api/v1/courses/", json=payload)
    assert res1.status_code == 201

    payload_duplicate = {
        "name": "CA Intermediate",
        "display_order": 2,
    }
    res2 = await async_client.post("/api/v1/courses/", json=payload_duplicate)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


# Test 3: Prevent duplicate display_order (400 Bad Request)
async def test_create_duplicate_display_order(async_client: AsyncClient):
    payload1 = {
        "name": "CA Foundation",
        "display_order": 1,
    }
    res1 = await async_client.post("/api/v1/courses/", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "name": "CA Final",
        "display_order": 1,
    }
    res2 = await async_client.post("/api/v1/courses/", json=payload2)
    assert res2.status_code == 400
    assert "Display order 1 is already taken" in res2.json()["detail"]


# Test 4: List all courses ordered by display_order (200 OK)
async def test_list_courses(async_client: AsyncClient):
    courses = [
        {"name": "CA Final", "display_order": 3},
        {"name": "CA Foundation", "display_order": 1},
        {"name": "CA Intermediate", "display_order": 2},
    ]
    for c in courses:
        res = await async_client.post("/api/v1/courses/", json=c)
        assert res.status_code == 201

    response = await async_client.get("/api/v1/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Check that they are ordered by display_order
    assert data[0]["name"] == "CA Foundation"
    assert data[1]["name"] == "CA Intermediate"
    assert data[2]["name"] == "CA Final"


# Test 5: Fetch course by ID (200 OK)
async def test_get_course_by_id(async_client: AsyncClient):
    payload = {"name": "CA Foundation", "display_order": 1}
    create_res = await async_client.post("/api/v1/courses/", json=payload)
    course_id = create_res.json()["id"]

    response = await async_client.get(f"/api/v1/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["id"] == course_id
    assert response.json()["name"] == "CA Foundation"


# Test 6: Fetch non-existent course returns 404 Not Found
async def test_get_course_not_found(async_client: AsyncClient):
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/courses/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# Test 7: Update course (200 OK)
async def test_update_course(async_client: AsyncClient):
    create_res = await async_client.post("/api/v1/courses/", json={"name": "CA Foundation", "display_order": 1})
    course_id = create_res.json()["id"]

    update_payload = {"display_order": 10}
    update_res = await async_client.put(f"/api/v1/courses/{course_id}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["display_order"] == 10


# Test 8: Delete course (204 No Content)
async def test_delete_course(async_client: AsyncClient):
    create_res = await async_client.post("/api/v1/courses/", json={"name": "CA Foundation", "display_order": 1})
    course_id = create_res.json()["id"]

    del_res = await async_client.delete(f"/api/v1/courses/{course_id}")
    assert del_res.status_code == 204

    # Verify it is deleted
    get_res = await async_client.get(f"/api/v1/courses/{course_id}")
    assert get_res.status_code == 404
