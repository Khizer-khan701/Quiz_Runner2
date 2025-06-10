from streamlit.testing.v1 import AppTest

def test_login_flow_with_mocked_auth(monkeypatch):
    # ✅ Mock Firestore user info retrieval
    mock_user_doc = {"name": "Test Teacher", "role": "Teacher"}
    monkeypatch.setattr("app.safe_get_user_info", lambda uid: mock_user_doc)

    # Initialize test app
    at = AppTest.from_file("app.py")
    at.run()  # First render

    # Fill in email and password inputs
    at.text_input("login_email").input("test@example.com")
    at.text_input("login_password").input("password123")

    # Click the Login button
    for button in at.get("button"):
        if button.label == "Login":
            button.click()
            break

    # ✅ Inject expected session state after login
    at.session_state["logged_in"] = True
    at.session_state["uid"] = "mock_uid_123"
    at.session_state["role"] = "Teacher"
    at.session_state["name"] = "Test Teacher"

    # Run app with updated session state
    at.run()

    # ✅ Verify sidebar greeting shows correct name
    sidebar_texts = [m.value for m in at.sidebar.markdown]
    print("Sidebar Texts:", sidebar_texts)
    assert any("Welcome, Test Teacher" in t for t in sidebar_texts)
    assert any("**Role:** Teacher" in t for t in sidebar_texts)
