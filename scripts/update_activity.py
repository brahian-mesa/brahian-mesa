"""Publish only public, authored commits from public repositories' default branches."""
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'brahian-mesa'
START = '<!-- ACTIVITY:START -->'
END = '<!-- ACTIVITY:END -->'

def api(path):
    headers = {'Accept':'application/vnd.github+json','User-Agent':'brahian-mesa-profile'}
    if token := os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer '+token
    request = urllib.request.Request('https://api.github.com/'+path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def collect(now, request=api):
    since = (now-timedelta(days=27)).replace(hour=0,minute=0,second=0,microsecond=0)
    commits = {}
    truncated = False
    for page in range(1,11):
        repos = request(f'users/{USER}/repos?type=owner&sort=pushed&per_page=100&page={page}')
        for repo in repos:
            if repo.get('private') or repo.get('fork') or repo.get('archived') or not repo.get('pushed_at'):
                continue
            if datetime.fromisoformat(repo['pushed_at'].replace('Z','+00:00')) < since:
                continue
            for batch in range(1,11):
                query = urllib.parse.urlencode({'author':USER,'since':since.isoformat(),'until':now.isoformat(),'per_page':100,'page':batch})
                rows = request(f"repos/{repo['full_name']}/commits?{query}")
                for row in rows:
                    if (row.get('author') or {}).get('login','').lower() != USER:
                        continue
                    date = row['commit']['author']['date']
                    stamp = datetime.fromisoformat(date.replace('Z','+00:00'))
                    if not since <= stamp <= now:
                        continue
                    key = row['sha']
                    # A SHA copied into another repository is counted once.
                    commits.setdefault(key, {'sha':key,'repository':repo['full_name'],'date':stamp.isoformat(),
                        'subject':row['commit']['message'].splitlines()[0], 'url':row['html_url']})
                if len(rows)<100:
                    break
                if batch==10:
                    truncated=True
        if len(repos)<100:
            break
        if page==10:
            truncated=True
    return {'from':since.date().isoformat(),'through':now.date().isoformat(),'timezone':'UTC',
            'scope':'public-owned-repositories-default-branches','truncated':truncated,
            'commits':sorted(commits.values(),key=lambda item:item['date'],reverse=True)}

def markdown_text(value):
    # Commit subjects are data, never Markdown/HTML instructions.
    value = ' '.join(value.split())[:115]
    return re.sub(r'([\\`*_[\]<>|])',r'\\\1',value)

def activity_markdown(data):
    rows = [f"**{len(data['commits'])} commits públicos** · {data['from']} → {data['through']} (UTC)", '',
            '![Actividad de commits públicos en los últimos 28 días](assets/activity.svg)', '',
            '**Últimos cambios**', '']
    for item in data['commits'][:6]:
        subject = markdown_text(item['subject'])
        rows.append(f"- `{item['date'][:10]}` · [{item['sha'][:7]}]({item['url']}) · **{item['repository']}** — {subject}")
    if not data['commits']:
        rows.append('No se encontraron commits públicos atribuibles a esta cuenta en este periodo.')
    if data['truncated']:
        rows.extend(['','Muestra limitada por paginación: el recuento puede ser parcial.'])
    rows.extend(['', 'Solo repositorios públicos propios y sus ramas predeterminadas. Se excluyen bots, forks y repositorios archivados. Los commits privados y los de organizaciones no forman parte de esta gráfica.', '',
                 '[Ver contribuciones del perfil](https://github.com/brahian-mesa?tab=overview) · [Historial del portafolio](https://github.com/brahian-mesa/portfolio/commits/main/)'])
    return '\n'.join(rows)

def svg(data):
    counts = Counter(item['date'][:10] for item in data['commits'])
    start = datetime.fromisoformat(data['from'])
    days = [(start+timedelta(days=i)).date().isoformat() for i in range(28)]
    maximum = max(counts.values(),default=1)
    bars = []
    for i,day in enumerate(days):
        count=counts[day]
        height = max(4,round(count/maximum*94))
        x=32+i*24
        fill='#a994f4' if count else '#323047'
        bars.append(f'<rect x="{x}" y="{158-height}" width="16" height="{height}" rx="4" fill="{fill}"><title>{day}: {count} commits</title></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="750" height="212" viewBox="0 0 750 212" role="img" aria-labelledby="title desc">
<title id="title">Commits públicos de {USER}</title><desc id="desc">Últimos 28 días, ramas predeterminadas de repositorios públicos propios. {len(data['commits'])} commits.</desc>
<rect width="750" height="212" rx="18" fill="#13111e"/>
<text x="32" y="32" font-family="Arial,sans-serif" font-size="13" fill="#c6b9e2">EVOLUCIÓN DE COMMITS PÚBLICOS</text>
<text x="718" y="32" text-anchor="end" font-family="Arial,sans-serif" font-size="12" fill="#83ded5">{len(data['commits'])} commits / 28 días</text>
{''.join(bars)}
<text x="32" y="188" font-family="Arial,sans-serif" font-size="11" fill="#b1a4c3">{escape(data['from'])}</text>
<text x="718" y="188" text-anchor="end" font-family="Arial,sans-serif" font-size="11" fill="#b1a4c3">{escape(data['through'])} · UTC</text>
</svg>'''

def write(data):
    path = ROOT/'README.md'
    readme = path.read_text(encoding='utf-8')
    if readme.count(START)!=1 or readme.count(END)!=1:
        raise ValueError('README activity markers must appear exactly once')
    block = START+'\n'+activity_markdown(data)+'\n'+END
    updated = re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:block,readme,flags=re.S)
    (ROOT/'assets').mkdir(exist_ok=True)
    (ROOT/'assets/activity.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'assets/activity.svg').write_text(svg(data),encoding='utf-8')
    path.write_text(updated,encoding='utf-8')

if __name__=='__main__':
    snapshot=collect(datetime.now(timezone.utc))
    write(snapshot)
    print(f"Published {len(snapshot['commits'])} public commits; scope: {snapshot['scope']}")
