import re
import os
import subprocess
import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE_DIR, "checklist_mestre_cdu_v0_a_v5.md")
HTML_PATH = os.path.join(BASE_DIR, "checklist_mestre_cdu_v0_a_v5.html")
PDF_PATH = os.path.join(BASE_DIR, "checklist_mestre_cdu_v0_a_v5.pdf")

def generate_mestre_pdf():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Pre-process markdown:
    # 1. Clean file:/// links to preserve code formatting and labels cleanly
    md_text = re.sub(r'\[([^\]]+)\]\(file:///[^\)]+\)', r'\1', md_text)
    
    # 2. Render markdown to HTML with proper table and tab indent support
    body_html = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code'],
        tab_length=2
    )

    # 3. Post-process checkboxes for interactive/printable view
    body_html = body_html.replace('<li>[ ]', '<li class="check-item"><span class="box-check">☐</span>')
    body_html = body_html.replace('<li>[x]', '<li class="check-item checked"><span class="box-check">☑</span>')
    body_html = body_html.replace('[x]', '<span class="badge badge-done">✓ CONCLUÍDO</span>')
    body_html = body_html.replace('[ ]', '<span class="badge badge-pending">⏳ A TESTAR</span>')

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SIGES — Checklist Mestre de Homologação (CDU V0 ao CDU V5)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #0284c7;
      --primary-dark: #0369a1;
      --primary-light: #e0f2fe;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --text-heading: #0f172a;
      --border-color: #e2e8f0;
      --bg-page: #f8fafc;
      --bg-card: #ffffff;
      --success-bg: #dcfce7;
      --success-text: #15803d;
      --success-border: #86efac;
      --warning-bg: #fef3c7;
      --warning-text: #b45309;
      --warning-border: #fde68a;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 11px;
      line-height: 1.5;
      color: var(--text-main);
      background-color: var(--bg-page);
      margin: 0;
      padding: 0;
    }}

    .container {{
      max-width: 1000px;
      margin: 20px auto;
      background: var(--bg-card);
      padding: 32px 40px;
      border-radius: 8px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    }}

    /* Compact Print Budgeting & Layout */
    @media print {{
      body {{
        background: #ffffff !important;
        font-size: 8pt !important;
        line-height: 1.3 !important;
      }}
      .container {{
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
      }}
      h1, h2, h3, h4 {{
        break-after: avoid !important;
        page-break-after: avoid !important;
      }}
      h2 {{
        break-before: auto !important;
        page-break-before: auto !important;
      }}
      table, .badge {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
      li.check-item {{
        break-inside: avoid;
        page-break-inside: avoid;
      }}
    }}

    @page {{
      size: A4 portrait;
      margin: 8mm 10mm 8mm 10mm;
      @bottom-right {{
        content: "Página " counter(page);
        font-size: 7.5pt;
        color: #64748b;
        font-family: 'Inter', sans-serif;
      }}
    }}

    .header-doc {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      border-bottom: 2px solid var(--primary);
      padding-bottom: 8px;
      margin-bottom: 10px;
      page-break-after: avoid;
      break-after: avoid;
    }}

    .header-title {{
      font-size: 15pt;
      font-weight: 800;
      color: var(--text-heading);
      letter-spacing: -0.02em;
      margin: 0;
    }}

    .header-subtitle {{
      font-size: 9pt;
      font-weight: 600;
      color: var(--primary);
      margin-top: 2px;
    }}

    .header-meta {{
      text-align: right;
      font-size: 7.5pt;
      color: var(--text-muted);
      line-height: 1.3;
    }}

    h1 {{
      font-size: 12pt;
      font-weight: 800;
      color: var(--text-heading);
      border-bottom: 1.5px solid var(--border-color);
      padding-bottom: 3px;
      margin-top: 10px;
      margin-bottom: 6px;
      page-break-after: avoid;
      break-after: avoid;
    }}

    h2 {{
      font-size: 9.5pt;
      font-weight: 700;
      color: #0369a1;
      background: #f0f9ff;
      border-left: 3.5px solid var(--primary);
      padding: 3px 8px;
      margin-top: 10px;
      margin-bottom: 5px;
      border-radius: 0 3px 3px 0;
      page-break-after: avoid;
      break-after: avoid;
    }}

    h3 {{
      font-size: 8.5pt;
      font-weight: 700;
      color: var(--text-heading);
      margin-top: 7px;
      margin-bottom: 3px;
      display: flex;
      align-items: center;
      gap: 5px;
      border-bottom: 1px dotted #e2e8f0;
      padding-bottom: 2px;
      page-break-after: avoid;
      break-after: avoid;
    }}

    p {{
      margin: 2px 0 4px 0;
    }}

    ul {{
      margin: 2px 0 4px 0;
      padding-left: 18px;
    }}

    ol {{
      margin: 2px 0 4px 0;
      padding-left: 18px;
    }}

    li {{
      margin-bottom: 1.5px;
    }}

    li.check-item {{
      list-style-type: none;
      position: relative;
      padding-left: 6px;
      font-size: 8pt;
      font-weight: 500;
      color: #334155;
    }}

    .box-check {{
      display: inline-block;
      width: 12px;
      font-size: 10pt;
      color: var(--primary);
      margin-right: 3px;
    }}

    li.checked .box-check {{
      color: #16a34a;
    }}

    code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      background: #f1f5f9;
      color: #0f172a;
      padding: 0.5px 3px;
      border-radius: 2px;
      border: 1px solid #e2e8f0;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 5px 0 8px 0;
      font-size: 7.5pt;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    th, td {{
      padding: 3px 5px;
      border: 1px solid var(--border-color);
      text-align: left;
    }}

    th {{
      background: #f1f5f9;
      font-weight: 700;
      color: #334155;
    }}

    tr:nth-child(even) {{
      background: #f8fafc;
    }}

    .badge {{
      display: inline-block;
      font-size: 7pt;
      font-weight: 700;
      padding: 0.5px 4px;
      border-radius: 2px;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }}

    .badge-done {{
      background: var(--success-bg);
      color: var(--success-text);
      border: 1px solid var(--success-border);
    }}

    .badge-pending {{
      background: var(--warning-bg);
      color: var(--warning-text);
      border: 1px solid var(--warning-border);
    }}

    hr {{
      border: none;
      border-top: 1px dashed var(--border-color);
      margin: 6px 0;
    }}

    blockquote {{
      background: #f0fdf4;
      border-left: 3px solid #22c55e;
      margin: 6px 0;
      padding: 4px 8px;
      color: #166534;
      font-size: 7.5pt;
      border-radius: 0 3px 3px 0;
    }}

    .footer-print {{
      margin-top: 12px;
      border-top: 1px solid var(--border-color);
      padding-top: 4px;
      display: flex;
      justify-content: space-between;
      font-size: 7pt;
      color: var(--text-muted);
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header-doc">
      <div>
        <div class="header-title">SIGES — Checklist Mestre de Homologação</div>
        <div class="header-subtitle">Consolidação Integral de Casos de Uso: do CDU V0 ao CDU V5</div>
      </div>
      <div class="header-meta">
        <div><strong>Status da Plataforma:</strong> 100% Implementado [x]</div>
        <div><strong>Data de Emissão:</strong> 28/09/2026</div>
        <div><strong>Escopo:</strong> Testes Ponta a Ponta (End-to-End)</div>
      </div>
    </div>

    {body_html}

    <div class="footer-print">
      <span>SIGES — Sistema de Gestão de Etapas de Serviços | Cosampa</span>
      <span>Roteiro Oficial de Homologação e Testes Operacionais (CDU V0 a V5)</span>
    </div>
  </div>
</body>
</html>
"""

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML gerado com sucesso em: {HTML_PATH}")

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser_exe = next((p for p in edge_paths if os.path.exists(p)), None)

    if browser_exe:
        print(f"Usando navegador: {browser_exe}")
        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("Retorno browser:", result.returncode)
        if os.path.exists(PDF_PATH):
            size = os.path.getsize(PDF_PATH)
            print(f"PDF criado com sucesso! Tamanho: {size} bytes ({size / 1024:.1f} KB)")
        else:
            print("Falha ao gerar PDF via headless.")
    else:
        print("Nenhum executável de navegador encontrado.")

if __name__ == "__main__":
    generate_mestre_pdf()
