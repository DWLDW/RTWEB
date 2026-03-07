def handle_logs_routes(path, user, conn, ctx):
    if path != "/logs":
        return None

    if not ctx["has_role"](user, [ctx["ROLE_OWNER"]]):
        return ctx["forbidden_html"](user)

    query = ctx.get("query", {})
    load_logs = query.get("load", "") == "1"

    ctx["ensure_logs_table"](conn)
    ctx["ensure_logs_columns"](conn)
    rows = conn.execute("SELECT id, level, route, user_id, message, detail, created_at FROM app_logs ORDER BY id DESC LIMIT 300").fetchall() if load_logs else []
    row_html = "".join([
        f"<tr><td>{r['id']}</td><td>{r['level']}</td><td>{r['route'] or '-'}</td><td>{r['user_id'] or '-'}</td><td>{r['message']}</td><td>{(r['detail'] or '-')}</td><td>{r['created_at']}</td></tr>"
        for r in rows
    ])
    html = ctx["render_html"](ctx["menu_t"]("logs"), f"""
    <div class='card'>
      <h4>{ctx['menu_t']('logs')}</h4>
      <form method='get' class='mobile-stack query-form' style='margin-bottom:8px'>
        <input type='hidden' name='lang' value='{query.get('lang', '')}'>
        <input type='hidden' name='load' value='1'>
        <div class='btn-row'>
          <button>{ctx['t']('common.search')}</button>
          <a class='btn secondary admin-action-link' data-preserve-scroll='1' href='/logs?lang={query.get('lang', '')}'>{ctx['t']('common.reset')}</a>
        </div>
      </form>
      {'' if load_logs else ("<div class='empty-msg'>" + ctx['t']('common.query_to_load') + "</div>")}
      <table>
        <tr><th>ID</th><th>level</th><th>route</th><th>user_id</th><th>message</th><th>detail</th><th>created_at</th></tr>
        {row_html if load_logs else ''}
        {(f"<tr><td colspan='7' class='empty-msg'>{ctx['t']('common.no_data')}</td></tr>") if (load_logs and not row_html) else ''}
      </table>
    </div>
    """, user, current_menu="logs")
    return ctx["text_resp"](html)