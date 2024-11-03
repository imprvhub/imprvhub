import os
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from github import Github


load_dotenv()
github_token = os.getenv('GH_TOKEN')

def get_languages_stats():
    try:
        g = Github(github_token)
        authenticated_user = g.get_user()
        language_repo_count = {}
        repo_count = 0        
        repos = authenticated_user.get_repos(affiliation='owner')
        
        for repo in repos:
            repo_count += 1
            try:
                repo_languages = repo.get_languages()
                for language in repo_languages.keys():
                    language_repo_count[language] = language_repo_count.get(language, 0) + 1                
            except Exception as e:
                print(f"   ⚠️ Error al procesar el repositorio {repo.name}: {str(e)}")
                print("-" * 50)
        language_percentages = {
            lang: (count / repo_count * 100)
            for lang, count in language_repo_count.items()
        }
        
        return language_percentages
    
    except Exception as e:
        print(f"Error de autenticación: {str(e)}")
        return {}

def create_language_svg(language_percentages):
    svg_width = 300
    svg_height = 400
    padding = 30
    bar_height = 10
    spacing = 30
    card_radius = 12
    text_offset = 15
    
    svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': str(svg_width),
        'height': str(svg_height),
        'viewBox': f'0 0 {svg_width} {svg_height}',
        'style': 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;'
    })
    
    style = ET.SubElement(svg, 'style')
    style.text = '''
        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .card { filter: drop-shadow(0px 4px 6px rgba(0, 0, 0, 0.1)); }
        .bar { animation: slideIn 1s ease-out forwards; }
        .text { animation: fadeIn 0.5s ease-out forwards; }
        .language { font-size: 12px; fill: currentColor; }
        .percentage { font-size: 12px; fill: currentColor; opacity: 0.8; }
    '''
    
    defs = ET.SubElement(svg, 'defs')
    
    light_gradient = ET.SubElement(defs, 'linearGradient', {
        'id': 'cardBgLight',
        'x1': '0%',
        'y1': '0%',
        'x2': '100%',
        'y2': '100%'
    })
    ET.SubElement(light_gradient, 'stop', {
        'offset': '0%',
        'style': 'stop-color:#ffffff;stop-opacity:1'
    })
    ET.SubElement(light_gradient, 'stop', {
        'offset': '100%',
        'style': 'stop-color:#f7f7f7;stop-opacity:1'
    })
    
    dark_gradient = ET.SubElement(defs, 'linearGradient', {
        'id': 'cardBgDark',
        'x1': '0%',
        'y1': '0%',
        'x2': '100%',
        'y2': '100%'
    })
    ET.SubElement(dark_gradient, 'stop', {
        'offset': '0%',
        'style': 'stop-color:#0d1117;stop-opacity:1'
    })
    ET.SubElement(dark_gradient, 'stop', {
        'offset': '100%',
        'style': 'stop-color:#161b22;stop-opacity:1'
    })
    
    script = ET.SubElement(svg, 'script')
    script.text = '''
        function updateTheme() {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const card = document.querySelector('.card-bg');
            const texts = document.querySelectorAll('.language, .percentage');
            if (isDark) {
                card.setAttribute('fill', 'url(#cardBgDark)');
                texts.forEach(t => t.setAttribute('fill', '#ffffff'));  // White text for dark mode
            } else {
                card.setAttribute('fill', 'url(#cardBgLight)');
                texts.forEach(t => t.setAttribute('fill', '#24292f'));
            }
        }
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', updateTheme);
            updateTheme();
        }
    '''
    
    card = ET.SubElement(svg, 'g', {'class': 'card'})
    ET.SubElement(card, 'rect', {
        'class': 'card-bg',
        'x': '0',
        'y': '0',
        'width': str(svg_width),
        'height': str(svg_height),
        'rx': str(card_radius),
        'fill': 'url(#cardBgLight)'
    })
    
    title = ET.SubElement(svg, 'text', {
        'x': str(padding + 25),
        'y': str(padding - 5),
        'class': 'text language',
        'style': 'font-size: 18px; font-weight: 600;'
    })
    title.text = 'Most Used Languages:'
    
    colors = {
        'Python': '#5E5E5E',
        'JavaScript': '#5E5E5E',
        'TypeScript': '#5E5E5E',
        'Vue': '#5E5E5E',
        'Astro': '#5E5E5E',
        'CSS': '#5E5E5E',
        'HTML': '#5E5E5E',
        'Java': '#5E5E5E',
        'SCSS': '#5E5E5E',
        'MDX': '#5E5E5E',
        'Shell': '#5E5E5E'
    }
    
    sorted_languages = sorted(
        language_percentages.items(),
        key=lambda x: x[1],
        reverse=True
    )[:8]
    
    y_position = padding + 20
    max_bar_width = svg_width - (padding * 3)
    
    for i, (lang, percentage) in enumerate(sorted_languages):
        delay = i * 0.1
        
        g = ET.SubElement(svg, 'g', {
            'transform': f'translate(0, {y_position})',
            'style': f'animation-delay: {delay}s'
        })
        
        lang_text = ET.SubElement(g, 'text', {
            'class': 'text language',
            'x': str(padding + 25),
            'y': '0',
            'dominant-baseline': 'middle',
            'style': f'animation-delay: {delay}s'
        })
        lang_text.text = lang
        
        ET.SubElement(g, 'rect', {
            'class': 'bar',
            'x': str(padding + 25),
            'y': str(text_offset),
            'width': str((percentage / 100) * max_bar_width),
            'height': str(bar_height),
            'rx': '4',
            'fill': colors.get(lang, '#8b949e'),
            'style': f'animation-delay: {delay}s'
        })
        
        percentage_text = ET.SubElement(g, 'text', {
            'class': 'text percentage',
            'x': str(padding + max_bar_width + 5),
            'y': str(text_offset + (bar_height / 2) + 2), 
            'text-anchor': 'end',
            'dominant-baseline': 'middle',
            'style': f'animation-delay: {delay}s'
        })
        percentage_text.text = f'{percentage:.1f}%'
        
        y_position += spacing + bar_height
    
    tree = ET.ElementTree(svg)
    tree.write('stats.svg', encoding='utf-8', xml_declaration=True)

def main():
    try:
        language_percentages = get_languages_stats()
        
        print("\nGenerando SVG...")
        create_language_svg(language_percentages)
        print("SVG generado como 'stats.svg'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()