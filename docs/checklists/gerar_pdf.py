import re
import os
import subprocess
import markdown

MD_PATH = r"c:\git\SIGES-SISTEMAS DE GESTAO DE ETAPAS DE SERVICOS\docs\checklists\checklist_completo_implementacao_cdu_v5.md"
HTML_PATH = r"c:\git\SIGES-SISTEMAS DE GESTAO DE ETAPAS DE SERVICOS\docs\checklists\checklist_completo_implementacao_cdu_v5.html"
PDF_PATH = r"c:\git\SIGES-SISTEMAS DE GESTAO DE ETAPAS DE SERVICOS\docs\checklists\checklist_completo_implementacao_cdu_v5.pdf"

def generate_pdf_report():
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

    # 3. Post-process badges for done and pending
    body_html = body_html.replace('[x]', '<span class="badge badge-done">✓ CONCLUÍDO</span>')
    body_html = body_html.replace('[ ]', '<span class="badge badge-pending">⏳ PENDENTE</span>')

    full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Checklist Geral de Implementação — SIGES (CDU V5)</title>
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
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 9pt;
      line-height: 1.4;
      color: var(--text-main);
      background-color: var(--bg-page);
      margin: 0;
      padding: 0;
    }}

    /* Screen Presentation Container */
    @media screen {{
      body {{
        padding: 32px 16px;
      }}
      .doc-wrapper {{
        max-width: 940px;
        margin: 0 auto;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
        padding: 40px 48px;
      }}
      .screen-actions {{
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-bottom: 20px;
      }}
      .btn-print {{
        background: var(--primary);
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 9pt;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: background 0.15s ease;
      }}
      .btn-print:hover {{
        background: var(--primary-dark);
      }}
    }}

    /* Print Budgeting & Rules */
    @media print {{
      @page {{
        size: A4 portrait;
        margin: 10mm 12mm 10mm 12mm;
        @bottom-right {{
          content: "Página " counter(page);
          font-size: 7.5pt;
          color: #64748b;
          font-family: 'Inter', sans-serif;
        }}
      }}
      body {{
        background-color: #ffffff;
        font-size: 8.5pt;
        line-height: 1.34;
      }}
      .doc-wrapper {{
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
        max-width: 100% !important;
      }}
      .screen-actions {{
        display: none !important;
      }}
    }}

    .header-banner {{
      border-bottom: 2.5px solid var(--primary);
      padding-bottom: 8px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      page-break-after: avoid;
      break-after: avoid;
    }}

    .header-title {{
      font-size: 16pt;
      font-weight: 800;
      color: var(--text-heading);
      margin: 0;
      letter-spacing: -0.4px;
    }}

    .header-subtitle {{
      font-size: 9pt;
      color: var(--primary);
      font-weight: 600;
      margin-top: 2px;
    }}

    .header-meta {{
      font-size: 8pt;
      color: var(--text-muted);
      text-align: right;
      font-weight: 500;
      line-height: 1.35;
    }}

    .header-meta strong {{
      color: var(--text-heading);
    }}

    h1 {{
      font-size: 13.5pt;
      color: var(--text-heading);
      border-bottom: 1.5px solid var(--border-color);
      padding-bottom: 4px;
      margin-top: 14px;
      margin-bottom: 8px;
      page-break-after: avoid;
      break-after: avoid;
    }}

    h2 {{
      font-size: 10.5pt;
      color: var(--primary-dark);
      background: var(--primary-light);
      border-left: 3.5px solid var(--primary);
      padding: 4px 10px;
      margin-top: 14px;
      margin-bottom: 6px;
      border-radius: 0 4px 4px 0;
      page-break-after: avoid;
      break-after: avoid;
    }}

    h3 {{
      font-size: 9pt;
      color: var(--text-heading);
      margin-top: 10px;
      margin-bottom: 4px;
      font-weight: 700;
      border-bottom: 1px dashed #cbd5e1;
      padding-bottom: 3px;
      page-break-after: avoid;
      break-after: avoid;
    }}

    p {{
      margin: 3px 0 5px 0;
    }}

    ul {{
      margin: 2px 0 6px 18px;
      padding: 0;
    }}

    ul ul {{
      margin: 2px 0 4px 16px;
    }}

    ol {{
      margin: 2px 0 6px 18px;
      padding: 0;
    }}

    li {{
      margin-bottom: 2.5px;
    }}

    code {{
      font-family: 'JetBrains Mono', Consolas, "Courier New", monospace;
      font-size: 7.5pt;
      background: #f1f5f9;
      color: #0f172a;
      padding: 1px 4px;
      border-radius: 3px;
      border: 1px solid #cbd5e1;
    }}

    strong {{
      font-weight: 600;
      color: var(--text-heading);
    }}

    a {{
      color: var(--primary);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    .badge {{
      display: inline-block;
      font-size: 7pt;
      font-weight: 700;
      padding: 1.5px 6px;
      border-radius: 4px;
      letter-spacing: 0.2px;
      vertical-align: 1px;
      text-transform: uppercase;
    }}

    .badge-done {{
      background-color: var(--success-bg);
      color: var(--success-text);
      border: 1px solid var(--success-border);
    }}

    .badge-pending {{
      background-color: var(--warning-bg);
      color: var(--warning-text);
      border: 1px solid var(--warning-border);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 8pt;
      margin: 8px 0 12px 0;
      page-break-inside: avoid;
      break-inside: avoid;
      background: #ffffff;
    }}

    th, td {{
      border: 1px solid #cbd5e1;
      padding: 5px 8px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background-color: #0f172a;
      color: #ffffff;
      font-weight: 700;
      font-size: 8pt;
    }}

    tr:nth-child(even) {{
      background-color: #f8fafc;
    }}

    hr {{
      border: none;
      border-top: 1px solid var(--border-color);
      margin: 12px 0;
    }}

    .footer-print {{
      margin-top: 18px;
      border-top: 1px solid #cbd5e1;
      padding-top: 8px;
      display: flex;
      justify-content: space-between;
      font-size: 7.5pt;
      color: var(--text-muted);
      page-break-inside: avoid;
      break-inside: avoid;
    }}
  </style>
</head>
<body>
  <div class="doc-wrapper">
    <div class="screen-actions">
      <button class="btn-print" onclick="window.print()">
        🖨️ Imprimir / Salvar PDF
      </button>
    </div>

    <div class="header-banner">
      <div>
        <div class="header-title">SIGES — Checklist de Implementação</div>
        <div class="header-subtitle">Confronto Técnico & Homologação com Especificação CDU V5</div>
      </div>
      <div class="header-meta">
        <div><strong>Status Oficial:</strong> Blocos 1, 2, 3 e 4 Concluídos [x]</div>
        <div><strong>Data de Emissão:</strong> 25/09/2026</div>
        <div><strong>Versão:</strong> 5.0 (Oficial)</div>
      </div>
    </div>

    {body_html}

    <div class="footer-print">
      <span>SIGES — Sistema de Gestão de Etapas de Serviços | Cosampa</span>
      <span>Documento Técnico Oficial para Impressão e Auditoria Operacional</span>
    </div>
  </div>
</body>
</html>
"""

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML gerado com sucesso em: {HTML_PATH}")

    # Compile to PDF using Headless Edge / Chrome
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
    generate_pdf_report()
