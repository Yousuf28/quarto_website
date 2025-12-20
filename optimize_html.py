#!/usr/bin/env python3
"""
Post-processing script to optimize Quarto-generated HTML files for performance.
This script should be run after 'quarto render' to optimize the generated HTML.
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Tuple

# #region agent log
LOG_PATH = "/Users/yousuf/Documents/not_in_icloud/00_github/quarto_website/.cursor/debug.log"
SERVER_ENDPOINT = "http://127.0.0.1:7242/ingest/0d8a3ffb-db0f-4d0d-bb77-1686141c3976"

def log_debug(hypothesis_id: str, message: str, data: dict, run_id: str = "optimize"):
    """Log debug information"""
    import urllib.request
    import urllib.error
    log_entry = {
        "location": "optimize_html.py",
        "message": message,
        "data": data,
        "timestamp": int(__import__('time').time() * 1000),
        "sessionId": "debug-session",
        "runId": run_id,
        "hypothesisId": hypothesis_id
    }
    try:
        req = urllib.request.Request(
            SERVER_ENDPOINT,
            data=json.dumps(log_entry).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=0.1)
    except:
        pass
    # Also write to file
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except:
        pass
# #endregion

def optimize_html_file(file_path: Path) -> Tuple[bool, dict]:
    """Optimize a single HTML file"""
    # #region agent log
    log_debug('C', 'Starting HTML optimization', {'file': str(file_path)})
    # #endregion
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        changes = {'scripts_deferred': 0, 'css_preloaded': 0, 'scripts_moved': 0, 'formatting_improved': 0}
        
        # Find head and body
        head = soup.find('head')
        body = soup.find('body')
        
        if not head or not body:
            # #region agent log
            log_debug('C', 'Missing head or body', {'file': str(file_path)})
            # #endregion
            return False, changes
        
        # Critical CSS files to preload
        critical_css = [
            'bootstrap.min.css',
            'bootstrap-icons.css',
            'quarto-syntax-highlighting-dark.css'
        ]
        
        # Scripts that can be deferred (non-critical)
        deferrable_scripts = [
            'quarto-nav.js',
            'headroom.min.js',
            'clipboard.min.js',
            'autocomplete.umd.js',
            'fuse.min.js',
            'quarto-search.js',
            'popper.min.js',
            'tippy.umd.min.js',
            'anchor.min.js',
            'list.min.js',
            'quarto-listing.js'
        ]
        
        # Scripts that must load in order and can be deferred
        # quarto.js and bootstrap.min.js should load after DOM is ready
        critical_but_deferrable = ['quarto.js', 'bootstrap.min.js']
        
        # Collect all script tags in head
        scripts_in_head = head.find_all('script', src=True)
        scripts_to_move = []
        scripts_to_defer_in_place = []
        
        for script in scripts_in_head:
            src = script.get('src', '')
            script_name = os.path.basename(src)
            
            # Check if this script can be deferred
            can_defer = any(ds in script_name for ds in deferrable_scripts + critical_but_deferrable)
            
            # Move non-critical scripts to end of body
            if any(ds in script_name for ds in deferrable_scripts):
                # Extract (remove from head) and add to move list
                extracted_script = script.extract()
                if can_defer and not extracted_script.get('defer') and not extracted_script.get('async'):
                    extracted_script['defer'] = True
                    changes['scripts_deferred'] += 1
                    # #region agent log
                    log_debug('C', 'Script deferred and moved', {'script': script_name, 'file': str(file_path)})
                    # #endregion
                scripts_to_move.append(extracted_script)
                changes['scripts_moved'] += 1
            elif can_defer and not script.get('defer') and not script.get('async'):
                # Defer but keep in head (critical scripts like quarto.js, bootstrap.min.js)
                script['defer'] = True
                changes['scripts_deferred'] += 1
                scripts_to_defer_in_place.append(script_name)
                # #region agent log
                log_debug('C', 'Script deferred in head', {'script': script_name, 'file': str(file_path)})
                # #endregion
        
        # Add moved scripts to end of body (before closing body tag, but before inline scripts)
        # Format scripts on separate lines for better parsing
        for script in scripts_to_move:
            # Insert before the last script (which is usually the inline DOMContentLoaded script)
            inline_scripts = body.find_all('script', src=False)
            if inline_scripts:
                inline_scripts[-1].insert_before(script)
                # Add newline after script for better formatting
                script.insert_after('\n')
            else:
                body.append(script)
                body.append('\n')
        
        # Add preload links for critical CSS with fetchpriority
        existing_preloads = {link.get('href', '') for link in head.find_all('link', rel='preload')}
        
        for link in head.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if any(css in href for css in critical_css):
                if href not in existing_preloads:
                    preload = soup.new_tag('link', rel='preload', href=href, as_='style')
                    # Add fetchpriority for critical CSS (Bootstrap is most critical)
                    if 'bootstrap.min.css' in href:
                        preload['fetchpriority'] = 'high'
                    # Insert preload before the stylesheet link
                    link.insert_before(preload)
                    changes['css_preloaded'] += 1
                    # #region agent log
                    log_debug('C', 'CSS preload added', {'css': href, 'file': str(file_path)})
                    # #endregion
                # Add fetchpriority to the actual stylesheet link for critical CSS
                if 'bootstrap.min.css' in href and not link.get('fetchpriority'):
                    link['fetchpriority'] = 'high'
        
        # Add resource hints (dns-prefetch for external resources if any)
        # Add preconnect for GitHub if there are GitHub links
        github_links = soup.find_all('a', href=re.compile(r'github\.com'))
        if github_links:
            existing_preconnects = {link.get('href', '') for link in head.find_all('link', rel='preconnect')}
            if 'https://github.com' not in existing_preconnects:
                preconnect = soup.new_tag('link', rel='preconnect', href='https://github.com')
                head.insert(1, preconnect)  # Insert early in head
        
        # Update or add performance monitoring script
        existing_perf_scripts = head.find_all('script', string=re.compile(r'performance\.now'))
        perf_script_content = """(function(){const perfData={startTime:performance.now(),navigationStart:performance.timing?.navigationStart||Date.now(),metrics:{}};const logPerf=(h,m,d)=>{fetch('http://127.0.0.1:7242/ingest/0d8a3ffb-db0f-4d0d-bb77-1686141c3976',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'optimized-html:head',message:m,data:d,timestamp:Date.now(),sessionId:'debug-session',runId:'optimized',hypothesisId:h})}).catch(()=>{});};logPerf('D','Page load started',{time:perfData.startTime});window.addEventListener('DOMContentLoaded',()=>{const domReady=performance.now()-perfData.startTime;logPerf('D','DOMContentLoaded',{time:domReady});const scripts=document.querySelectorAll('script[src]');scripts.forEach((s,i)=>{s.addEventListener('load',()=>logPerf('D','Script loaded',{index:i,src:s.src,time:performance.now()-perfData.startTime,deferred:!!s.defer}));});});window.addEventListener('load',()=>{const loadTime=performance.now()-perfData.startTime;logPerf('D','Window load complete',{time:loadTime});if(performance.getEntriesByType){const resources=performance.getEntriesByType('resource');resources.forEach(r=>logPerf('E','Resource loaded',{name:r.name,duration:r.duration,size:r.transferSize||0}));}});})();"""
        
        if existing_perf_scripts:
            # Update existing performance script to use 'optimized' runId
            for perf_script in existing_perf_scripts:
                old_content = perf_script.string or ''
                # Replace runId from 'baseline' to 'optimized' and update hypothesis IDs
                new_content = old_content.replace("runId:'baseline'", "runId:'optimized'")
                new_content = new_content.replace("runId:\"baseline\"", "runId:\"optimized\"")
                new_content = new_content.replace("hypothesisId:'A'", "hypothesisId:'D'")
                new_content = new_content.replace("hypothesisId:\"A\"", "hypothesisId:\"D\"")
                new_content = new_content.replace("hypothesisId:'B'", "hypothesisId:'E'")
                new_content = new_content.replace("hypothesisId:\"B\"", "hypothesisId:\"E\"")
                perf_script.string = new_content
                # #region agent log
                log_debug('C', 'Updated performance script', {'file': str(file_path)})
                # #endregion
        else:
            # Add new performance monitoring script
            perf_script = soup.new_tag('script')
            perf_script.string = perf_script_content
            # Insert after viewport meta tag
            viewport = head.find('meta', attrs={'name': 'viewport'})
            if viewport:
                viewport.insert_after(perf_script)
            else:
                head.insert(1, perf_script)
            # #region agent log
            log_debug('C', 'Added performance script', {'file': str(file_path)})
            # #endregion
        
        # Ensure critical scripts load in correct order
        # quarto.js should load before bootstrap.min.js
        quarto_script = head.find('script', src=re.compile(r'quarto\.js'))
        bootstrap_script = head.find('script', src=re.compile(r'bootstrap\.min\.js'))
        
        if quarto_script and bootstrap_script:
            # Ensure quarto.js comes before bootstrap.min.js
            quarto_pos = list(head.children).index(quarto_script) if quarto_script.parent == head else -1
            bootstrap_pos = list(head.children).index(bootstrap_script) if bootstrap_script.parent == head else -1
            if quarto_pos > bootstrap_pos and quarto_pos > 0:
                bootstrap_script.insert_before(quarto_script)
        
        # Optimize inline script execution
        inline_scripts = body.find_all('script', src=False)
        for script in inline_scripts:
            script_content = script.string or ''
            # If script uses DOMContentLoaded, optimize it
            if 'DOMContentLoaded' in script_content:
                # Check if we can make it async by wrapping in requestIdleCallback or setTimeout
                # For now, ensure it's at the very end and add type="module" if appropriate
                script.extract()
                # Add defer attribute if the script doesn't need immediate execution
                # Most DOMContentLoaded handlers can wait
                if not script.get('defer') and not script.get('async'):
                    # Keep it synchronous but ensure it's last
                    pass
                body.append(script)
                body.append('\n')
        
        # Format HTML for better readability and parsing
        optimized_html = str(soup)
        
        # Post-process: Always apply formatting improvements
        # Ensure scripts are on separate lines (helps with parsing and browser optimization)
        optimized_html = re.sub(
            r'(</script>)(<script[^>]*>)',
            r'\1\n\2',
            optimized_html
        )
        # Also fix script tags that are immediately adjacent without space
        optimized_html = re.sub(
            r'(<script[^>]*>)(<script[^>]*>)',
            r'\1\n\2',
            optimized_html
        )
        
        # Always count formatting as a change if we modified the HTML
        formatting_applied = optimized_html != str(soup)
        if formatting_applied:
            changes['formatting_improved'] = 1
        
        # #region agent log
        log_debug('C', 'Optimization complete', {'changes': changes, 'file': str(file_path), 'formatting_applied': formatting_applied})
        # #endregion
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(optimized_html)
        
        return True, changes
        
    except Exception as e:
        # #region agent log
        log_debug('C', 'Optimization error', {'error': str(e), 'file': str(file_path)})
        # #endregion
        return False, {}

def main():
    """Main function to optimize all HTML files"""
    # #region agent log
    log_debug('C', 'Starting optimization process', {})
    # #endregion
    
    docs_dir = Path(__file__).parent / 'docs'
    
    if not docs_dir.exists():
        # #region agent log
        log_debug('C', 'Docs directory not found', {'path': str(docs_dir)})
        # #endregion
        print(f"Error: {docs_dir} does not exist")
        return
    
    html_files = list(docs_dir.rglob('*.html'))
    
    # #region agent log
    log_debug('C', 'Found HTML files', {'count': len(html_files)})
    # #endregion
    
    total_changes = {'scripts_deferred': 0, 'css_preloaded': 0, 'scripts_moved': 0, 'formatting_improved': 0}
    optimized_count = 0
    
    for html_file in html_files:
        success, changes = optimize_html_file(html_file)
        if success:
            optimized_count += 1
            for key in total_changes:
                total_changes[key] += changes.get(key, 0)
    
    # #region agent log
    log_debug('C', 'Optimization summary', {'optimized': optimized_count, 'total': len(html_files), 'changes': total_changes})
    # #endregion
    
    print(f"Optimized {optimized_count}/{len(html_files)} HTML files")
    print(f"  - Scripts deferred: {total_changes['scripts_deferred']}")
    print(f"  - CSS preloaded: {total_changes['css_preloaded']}")
    print(f"  - Scripts moved to body: {total_changes['scripts_moved']}")
    print(f"  - Formatting improved: {total_changes['formatting_improved']}")

if __name__ == '__main__':
    main()

