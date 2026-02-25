def render_report_html(data):
    params_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data["asl_parameters"])
    missing_html = "".join(f"<li>{param}</li>" for param in data["missing_parameters"])
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
        <p>{data["basic_report"]}</p>
        <h2>Extended Report</h2>
        <p>{data["extended_report"]}</p>
        <h2>Missing Parameters</h2>
        <ul>
            {missing_html}
        </ul>
    </body>
    </html>
    """
