
def handle_auth_routes(path, method, environ, ctx):
    if path == "/login":
        if method == "GET":
            html = ctx["render_html"](ctx["t"]("login.title"), f"""
            <form method='post'>
              <div>{ctx['t']('login.username')} <input name='username'></div>
              <div>{ctx['t']('login.password')} <input name='password' type='password'></div>
              <button type='submit'>{ctx['t']('common.login')}</button>
            </form>
            <p>{ctx['t']('login.default_accounts')}</p>
            """)
            return ctx["text_resp"](html)

        data = ctx["parse_body"](environ)
        conn = ctx["get_db"]()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password_hash=?",
            (data.get("username", ""), ctx["hash_pw"](data.get("password", ""))),
        ).fetchone()
        if not user:
            conn.close()
            html = ctx["render_html"](ctx["t"]("login.title"), f"<p style='color:red'>{ctx['t']('login.failed')}</p>")
            return ctx["text_resp"](html, "401 Unauthorized")

        token = str(ctx["uuid"].uuid4())
        conn.execute("INSERT INTO sessions(user_id, token, created_at) VALUES(?,?,?)", (user["id"], token, ctx["now"]()))
        conn.commit()
        conn.close()
        status, headers, body = ctx["redirect"]('/dashboard')
        headers.append(("Set-Cookie", f"session={token}; Path=/; HttpOnly"))
        return status, headers, body

    if path == "/logout":
        status, headers, body = ctx["redirect"]('/login')
        headers.append(("Set-Cookie", "session=; Path=/; Max-Age=0"))
        return status, headers, body

    return None
