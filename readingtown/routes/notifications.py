
def handle_notifications_routes(path, method, environ, user, conn, ctx):
    if path != "/announcements":
        return None

    if method == "POST" and ctx["has_role"](user, [ctx["ROLE_OWNER"], ctx["ROLE_MANAGER"], ctx["ROLE_TEACHER"]]):
        d = ctx["parse_body"](environ)
        conn.execute(
            "INSERT INTO announcements(title, content, created_by, created_at) VALUES(?,?,?,?)",
            (d.get("title"), d.get("content"), user["id"], ctx["now"]()),
        )
        conn.commit()

    rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
    noti = conn.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()
    ann_rows = "".join([
        f"<tr><td>{r['id']}</td><td>{r['title']}</td><td>{r['content']}</td><td>{r['created_by']}</td><td>{r['created_at']}</td></tr>"
        for r in rows
    ])
    noti_rows = "".join([
        f"<tr><td>{r['id']}</td><td>{r['type']}</td><td>{r['target_user_id'] or '-'}</td><td>{r['payload']}</td><td>{r['created_at']}</td></tr>"
        for r in noti
    ])
    html = ctx["render_html"](ctx["t"]("ann.title"), f"""
    <div class='card'><h4>{ctx['t']("ann.write")}</h4><form method='post' class='form-row'>{ctx['t']("field.title")}<input name='title'> {ctx['t']('field.content')}<input name='content'><button>{ctx['t']('common.save')}</button></form></div>
    <div class='card'><h4>{ctx['t']("ann.list")}</h4><table><tr><th>{ctx['t']("field.id")}</th><th>{ctx['t']("field.title")}</th><th>{ctx['t']("field.content")}</th><th>{ctx['t']("field.writer")}</th><th>{ctx['t']("field.created_at")}</th></tr>{ann_rows or f"<tr><td colspan='5' class='empty-msg'>{ctx['t']('common.no_data')}</td></tr>"}</table></div>
    <div class='card'><h4>{ctx['t']("ann.noti")}</h4><table><tr><th>{ctx['t']("field.id")}</th><th>{ctx['t']("field.type")}</th><th>{ctx['t']("field.target")}</th><th>{ctx['t']("field.data")}</th><th>{ctx['t']("field.created_at")}</th></tr>{noti_rows or f"<tr><td colspan='5' class='empty-msg'>{ctx['t']('common.no_data')}</td></tr>"}</table></div>
    """, user, current_menu="announcements")
    return ctx["text_resp"](html)
