
def handle_api_routes(path, method, environ, user, conn, ctx):
    if path == "/api/auth/login" and method == "POST":
        data = ctx["parse_body"](environ)
        auth_conn = ctx["get_db"]()
        found_user = auth_conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), ctx["hash_pw"](data.get("password", ""))),
        ).fetchone()
        if not found_user:
            auth_conn.close()
            return ctx["json_resp"]({"error": ctx["t"]('login.failed')}, "401 Unauthorized")
        token = str(ctx["uuid"].uuid4())
        auth_conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (found_user["id"], token, ctx["now"]()))
        auth_conn.commit()
        auth_conn.close()
        status, headers, body = ctx["json_resp"]({"message": "ok", "role": found_user["role"]})
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        return status, headers, body

    if path == "/api/announcements" and method == "GET" and conn is not None:
        rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
        return ctx["json_resp"]([dict(r) for r in rows])

    return None

