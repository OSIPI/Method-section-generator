def render_report_html(data):
    # Support asl_parameters as either list of tuples or dict
    asl_params = data.get("asl_parameters", [])
    if isinstance(asl_params, dict):
        asl_params = list(asl_params.items())
    params_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in asl_params)

    # Support both 'missing_parameters' (template key) and 'missing_required_parameters' (processor key)
    missing = data.get("missing_parameters", data.get("missing_required_parameters", []))
    if isinstance(missing, dict):
        missing = list(missing.keys())
    missing_html = "".join(f"<li>{param}</li>" for param in missing)

    basic_report = data.get("basic_report", "")
    extended_report = data.get("extended_report", "")

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
            th, td {{ padding: 8px; }}
        </style>
    </head>
    <body>
        <h1>ASL Report</h1>
        <h2>Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            {params_html}
        </table>
        <h2>Basic Report</h2>
        <p>{basic_report}</p>
        <h2>Extended Report</h2>
        <p>{extended_report}</p>
        <h2>Missing Parameters</h2>
        <ul>
            {missing_html}
        </ul>
    </body>
    </html>
    """

