
def handle_auth_routes(path, method, environ, ctx):
    if path == "/login":
        if method == "GET":
            html = ctx["render_html"](ctx["t"]("login.title"), f"""
            <form method='post'>
              <div>{ctx['t']('login.username')} <input name='username'></div>
              <div>{ctx['t']('login.password')} <input name='password' type='password'></div>
              <button type='submit'>{ctx['t']('common.login')}</button>
            </form>
            """)
            return ctx["text_resp"](html)

        data = ctx["parse_body"](environ)
        conn = ctx["get_db"]()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (data.get("username", ""),),
        ).fetchone()
        password = data.get("password", "")
        if not user or not ctx["verify_pw"](password, user["password_hash"]):
            conn.close()
            html = ctx["render_html"](ctx["t"]("login.title"), f"<p style='color:red'>{ctx['t']('login.failed')}</p>")
            return ctx["text_resp"](html, "401 Unauthorized")

        if ctx["needs_password_rehash"](user["password_hash"]):
            conn.execute("UPDATE users SET password_hash=? WHERE id=?", (ctx["hash_pw"](password), user["id"]))

        token = ctx["create_session"](conn, user["id"])
        conn.commit()
        conn.close()
        status, headers, body = ctx["redirect"]('/dashboard')
        headers.append(("Set-Cookie", ctx["build_session_cookie"](token, environ)))
        return status, headers, body

    if path == "/logout":
        cookies = ctx["parse_cookie"](environ.get("HTTP_COOKIE", ""))
        token = cookies.get("session")
        conn = ctx["get_db"]()
        ctx["invalidate_session"](conn, token)
        conn.commit()
        conn.close()
        status, headers, body = ctx["redirect"]('/login')
        headers.append(("Set-Cookie", ctx["clear_session_cookie"](environ)))
        return status, headers, body

    return None
