
def handle_logs_routes(path, user, conn, ctx):
    if path != "/logs":
        return None

    if not ctx["has_role"](user, [ctx["ROLE_OWNER"]]):
        return ctx["forbidden_html"](user)

    ctx["ensure_logs_table"](conn)
    ctx["ensure_logs_columns"](conn)
    rows = conn.execute("SELECT id, level, route, user_id, message, detail, created_at FROM app_logs ORDER BY id DESC LIMIT 300").fetchall()
    row_html = "".join([
        f"<tr><td>{r['id']}</td><td>{r['level']}</td><td>{r['route'] or '-'}</td><td>{r['user_id'] or '-'}</td><td>{r['message']}</td><td>{(r['detail'] or '-')}</td><td>{r['created_at']}</td></tr>"
        for r in rows
    ])
    html = ctx["render_html"](ctx["menu_t"]("logs"), f"""
    <div class='card'>
      <h4>{ctx['menu_t']('logs')}</h4>
      <table>
        <tr><th>ID</th><th>level</th><th>route</th><th>user_id</th><th>message</th><th>detail</th><th>created_at</th></tr>
        {row_html or f"<tr><td colspan='7' class='empty-msg'>{ctx['t']('common.no_data')}</td></tr>"}
      </table>
    </div>
    """, user, current_menu="logs")
    return ctx["text_resp"](html)
