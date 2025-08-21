#!/usr/bin/env python3
"""Generate test summary report with export capabilities."""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union, Optional

project_root = Path(__file__).parent.parent.parent 
tests_path = project_root
src_path = project_root / "src"
app_path = project_root / "app"

for path in [str(tests_path), str(src_path), str(app_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from tests import run_test_suite

try:
    from earth import __version__ as earth_version
except ImportError:
    earth_version = "unknown"

class TestReportExporter:
    """Handles exporting test reports in various formats.
    Supported formats: [html, json, markdown]"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "logs" / "test" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def _write_to_file(self, path: Path, content: str, variant: str, operation: Optional[str]='r', encoding: Optional[str]='utf-8') -> None:
        """Helper to write supported file types to disk"""
        with open(path, operation, encoding=encoding) as f:
            print(f'f is type: {type(f)}')
            print(f'Writing type: {type}')
            if variant in ['html', 'markdown']:
                f.write(content)
            elif variant in ['json']:
                json.dump(content, f, indent=2)
            else:
                raise ValueError(f'Received unsupported write type: {type}')
            
    def export_html(self, results: Union[Dict[str, bool], bool], timestamp: datetime, write_latest: bool = False) -> Path:
        """Export test results as HTML report."""
        html_content = self._generate_html_report(results, timestamp)
        
        # Write timestamped file
        filename = f"test_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.reports_dir / filename
        
        self._write_to_file(filepath, html_content, operation='w', variant='html')
        
        # Write latest file if requested
        if write_latest:
            latest_dir = self.reports_dir / "latest"
            latest_dir.mkdir(parents=True, exist_ok=True)
            latest_path = latest_dir / "latest.html"

            self._write_to_file(latest_path, html_content, operation='w', variant='html')
            
        return filepath
    
    def export_json(self, results: Union[Dict[str, bool], bool], timestamp: datetime, write_latest: bool = False) -> Path:
        """Export test results as JSON report."""
        json_content = {
            "timestamp": timestamp.isoformat(),
            "earth_version": earth_version,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "test_results": results if isinstance(results, dict) else {"all_tests": results},
            "summary": self._generate_summary(results)
        }
        
        # Write timestamped file
        filename = f"test_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.reports_dir / filename
        
        self._write_to_file(filepath, json_content, operation='w', variant='json')
        
        # Write latest file if requested
        if write_latest:
            latest_dir = self.reports_dir / "latest"
            latest_dir.mkdir(parents=True, exist_ok=True)
            latest_path = latest_dir / "latest.json"

            self._write_to_file(latest_path, json_content, operation='w', variant='json')
            
        return filepath
    

    def export_markdown(self, results: Union[Dict[str, bool], bool], timestamp: datetime, write_latest: bool = False) -> Path:
        """Export test results as Markdown report."""
        md_content = self._generate_markdown_report(results, timestamp)
        
        # Write timestamped file
        filename = f"test_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.reports_dir / filename

        self._write_to_file(filepath, md_content, operation='w', variant='markdown')

        
        # Write latest file if requested
        if write_latest:
            latest_dir = self.reports_dir / "latest"
            latest_dir.mkdir(parents=True, exist_ok=True)
            latest_path = latest_dir / "latest.md"
            self._write_to_file(latest_path, md_content, operation='w', variant='markdown')

        return filepath
    
    def _generate_html_report(self, results: Union[Dict[str, bool], bool], timestamp: datetime) -> str:
        """Generate HTML report content."""
        summary = self._generate_summary(results)
        
        # Determine overall status
        overall_success = summary["passed"] == summary["total"]
        status_color = "#28a745" if overall_success else "#dc3545"
        status_text = "PASSED" if overall_success else "FAILED"
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Earth Data Generator - Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 1.1em;
            background-color: {status_color};
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }}
        .stat-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        .results-table {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .results-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .results-table th {{
            background: #343a40;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        .results-table td {{
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        .results-table tr:last-child td {{
            border-bottom: none;
        }}
        .results-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .status-pass {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-fail {{
            color: #dc3545;
            font-weight: bold;
        }}
        .icon {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Earth Data Generator</h1>
        <p>Test Execution Report</p>
    </div>
    
    <div class="summary-card">
        <h2>📊 Test Summary</h2>
        <div style="margin: 20px 0;">
            <span class="status-badge">{status_text}</span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{summary["total"]}</div>
                <div class="stat-label">Total Categories</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #28a745;">{summary["passed"]}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #dc3545;">{summary["failed"]}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{summary["success_rate"]:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
    </div>
    
    <div class="results-table">
        <table>
            <thead>
                <tr>
                    <th>Test Category</th>
                    <th>Status</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_html_rows(results)}
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>Generated on {timestamp.strftime("%Y-%m-%d at %H:%M:%S")} | Earth v{earth_version} | Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}</p>
    </div>
</body>
</html>"""
        return html_template
    
    def _generate_html_rows(self, results: Union[Dict[str, bool], bool]) -> str:
        """Generate HTML table rows for test results."""
        rows = []
        
        if isinstance(results, dict):
            for category, success in results.items():
                status_class = "status-pass" if success else "status-fail"
                icon = "✅" if success else "❌"
                status_text = "PASSED" if success else "FAILED"
                
                rows.append(f"""
                <tr>
                    <td><strong>{category.upper()}</strong></td>
                    <td><span class="icon">{icon}</span></td>
                    <td><span class="{status_class}">{status_text}</span></td>
                </tr>""")
        else:
            status_class = "status-pass" if results else "status-fail"
            icon = "✅" if results else "❌"
            status_text = "PASSED" if results else "FAILED"
            
            rows.append(f"""
            <tr>
                <td><strong>ALL TESTS</strong></td>
                <td><span class="icon">{icon}</span></td>
                <td><span class="{status_class}">{status_text}</span></td>
            </tr>""")
        
        return "\n".join(rows)
    
    def _generate_markdown_report(self, results: Union[Dict[str, bool], bool], timestamp: datetime) -> str:
        """Generate Markdown report content."""
        summary = self._generate_summary(results)
        
        md_content = f"""# 🌍 Earth Data Generator - Test Report

**Generated:** {timestamp.strftime("%Y-%m-%d at %H:%M:%S")}  
**Earth Version:** {earth_version}  
**Python Version:** {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}

## 📊 Summary

- **Total Categories:** {summary["total"]}
- **Passed:** {summary["passed"]} ✅
- **Failed:** {summary["failed"]} ❌
- **Success Rate:** {summary["success_rate"]:.1f}%

## 📋 Detailed Results

| Test Category | Status | Result |
|---------------|---------|---------|
"""
        
        if isinstance(results, dict):
            for category, success in results.items():
                icon = "✅" if success else "❌"
                status = "PASSED" if success else "FAILED"
                md_content += f"| {category.upper()} | {icon} | **{status}** |\n"
        else:
            icon = "✅" if results else "❌"
            status = "PASSED" if results else "FAILED"
            md_content += f"| ALL TESTS | {icon} | **{status}** |\n"
        
        md_content += f"""
## 🔍 Test Environment

- **Project Root:** `{self.project_root}`
- **Reports Directory:** `{self.reports_dir}`
- **Timestamp:** {timestamp.isoformat()}

---
*Report generated by Earth Data Generator test suite*
"""
        
        return md_content
    
    def _generate_summary(self, results: Union[Dict[str, bool], bool]) -> Dict[str, Any]:
        """Generate summary statistics."""
        if isinstance(results, dict):
            total = len(results)
            passed = sum(1 for success in results.values() if success)
            failed = total - passed
        else:
            total = 1
            passed = 1 if results else 0
            failed = 1 - passed
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate
        }

def main():
    """Generate and display test summary report with export options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test summary report")
    parser.add_argument('--export', choices=['html', 'json', 'markdown', 'all'], 
                       help='Export format(s)')
    parser.add_argument('--quiet', '-q', action='store_true', 
                       help='Only show export paths, no console output')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🔄 Running test suite for summary report...")
    
    results = run_test_suite(verbose=False)
    timestamp = datetime.now()
    
    # Console output
    if not args.quiet:
        print('\n📊 Test Summary Report:')
        print('=' * 40)
        
        if isinstance(results, dict):
            # results is a dict of {category: bool}
            for cat, success in results.items():
                status = "PASS" if success else "FAIL"
                icon = "✅" if success else "❌"
                print(f'  {icon} {cat.upper()}: {status}')
            
            # Overall summary
            total_passed = sum(1 for success in results.values() if success)
            total_categories = len(results)
            
            print(f'\n📈 Overall: {total_passed}/{total_categories} categories passed')
            
            if total_passed == total_categories:
                print('🎉 All test categories passed!')
            else:
                failed_categories = [cat for cat, success in results.items() if not success]
                print(f'⚠️  Failed categories: {", ".join(failed_categories)}')
        
        elif isinstance(results, bool):
            # results is just a boolean
            status = "PASS" if results else "FAIL"
            icon = "✅" if results else "❌"
            print(f'  {icon} ALL TESTS: {status}')
        
        else:
            print('❌ Unexpected results format from test suite')
    
    # Export functionality
    if args.export:
        exporter = TestReportExporter(project_root)
        
        export_formats = [args.export] if args.export != 'all' else ['html', 'json', 'markdown']
        exported_files = []
        
        for fmt in export_formats:
            try:
                if fmt == 'html':
                    filepath = exporter.export_html(results, timestamp, write_latest=True)
                elif fmt == 'json':
                    filepath = exporter.export_json(results, timestamp, write_latest=True)
                elif fmt == 'markdown':
                    filepath = exporter.export_markdown(results, timestamp, write_latest=True)
                
                exported_files.append((fmt.upper(), filepath))
                
            except Exception as e:
                print(f"❌ Error exporting {fmt.upper()} report: {e}")
        
        # Show export results
        if exported_files:
            print(f'\n📁 Exported {len(exported_files)} report(s):')
            for fmt, filepath in exported_files:
                print(f'  📄 {fmt}: {filepath}')
            
            # Show latest files
            latest_dir = exporter.reports_dir / "latest"
            if latest_dir.exists():
                latest_files = list(latest_dir.glob("latest.*"))
                if latest_files:
                    print(f'\n🔗 Latest reports available:')
                    for latest_file in latest_files:
                        file_size = latest_file.stat().st_size
                        print(f'  📄 {latest_file} ({file_size} bytes)')
                    print(f'📁 Latest directory: {latest_dir}')

if __name__ == '__main__':
    main()