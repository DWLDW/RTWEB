
def handle_api_routes(path, method, environ, user, conn, ctx):
    if path == "/api/auth/login" and method == "POST":
        data = ctx["parse_body"](environ)
        auth_conn = ctx["get_db"]()
        found_user = auth_conn.execute(
            "SELECT * FROM users WHERE username=?",
            (data.get("username", ""),),
        ).fetchone()
        password = data.get("password", "")
        if not found_user or not ctx["verify_pw"](password, found_user["password_hash"]):
            auth_conn.close()
            return ctx["json_resp"]({"error": ctx["t"]('login.failed')}, "401 Unauthorized")
        if ctx["needs_password_rehash"](found_user["password_hash"]):
            auth_conn.execute("UPDATE users SET password_hash=? WHERE id=?", (ctx["hash_pw"](password), found_user["id"]))
        token = ctx["create_session"](auth_conn, found_user["id"])
        auth_conn.commit()
        auth_conn.close()
        status, headers, body = ctx["json_resp"]({"message": "ok", "role": found_user["role"]})
        headers.append(("Set-Cookie", ctx["build_session_cookie"](token, environ)))
        return status, headers, body

    if path == "/api/announcements" and method == "GET" and conn is not None:
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        return ctx["json_resp"]([dict(r) for r in rows])

    return None

