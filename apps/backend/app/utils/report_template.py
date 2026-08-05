def render_report_html(data):
    # 1. Safely handle asl_parameters (whether it's a dict or a list)
    asl_params = data.get("asl_parameters", {})
    if isinstance(asl_params, dict):
        params_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in asl_params.items())
    else:
        params_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in asl_params)

    # 2. Safely get missing parameters (checking both the new and old key names)
    missing_params = data.get("missing_required_parameters", data.get("missing_parameters", []))
    missing_html = "".join(f"<li>{param}</li>" for param in missing_params)
    
    # 3. Safely get the reports with a fallback default string
    basic_report = data.get("basic_report", "No basic report available.")
    extended_report = data.get("extended_report", "No extended report available.")

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