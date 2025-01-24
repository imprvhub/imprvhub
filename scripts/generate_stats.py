import os
import xml.etree.ElementTree as ET
from collections import Counter

from dotenv import load_dotenv
from github import Github

load_dotenv()
github_token = os.getenv('GH_TOKEN')

def get_languages_stats():
    try:
        g = Github(github_token)
        authenticated_user = g.get_user()
        language_repo_count = Counter()
        repos = authenticated_user.get_repos(affiliation='owner')

        for repo in repos:
            try:
                repo_languages = repo.get_languages()
                for language in repo_languages.keys():
                    if language.upper() in ['CSS', 'HTML', 'JAVASCRIPT']:
                        normalized_language = 'Vanilla JS/React.js'
                    elif language.upper() in ['GO', 'GOLANG']:
                        normalized_language = 'Go'
                    else:
                        normalized_language = language
                    language_repo_count[normalized_language] += 1
            except Exception as e:
                print(f"   ⚠️ Error al procesar el repositorio {repo.name}: {str(e)}")
                print("-" * 50)

        most_common = dict(language_repo_count.most_common(10))
        total_top_10 = sum(most_common.values())

        normalized_percentages = {}
        remaining = 100.0 

        languages = list(most_common.items())
        for lang, count in languages[:-1]:
            percentage = round((count / total_top_10 * 100), 1)
            normalized_percentages[lang] = percentage
            remaining -= percentage

        last_lang = languages[-1][0]
        normalized_percentages[last_lang] = round(remaining, 1)
        
        for lang, percentage in sorted(normalized_percentages.items(), key=lambda x: x[1], reverse=True):
            print(f"{lang}: {percentage:.1f}%")

        return normalized_percentages

    except Exception as e:
        print(f"Authentication Error: {str(e)}")
        return {}
    
def create_language_svg(language_percentages):
    svg_width = 300
    svg_height = 470
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
        'style': 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;',
        'data-color-mode': 'light dark'
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
        .language { font-size: 12px; }
        .percentage { font-size: 12px; opacity: 0.8; }

        @media (prefers-color-scheme: dark) {
            .card-bg { fill: #0d1117 !important; }
            .language, .percentage { fill: #ffffff !important; }
            .bar-color { fill: #9f9178 !important; }
        }

        @media (prefers-color-scheme: light) {
            .card-bg { fill: #ffffff !important; }
            .language, .percentage { fill: #24292f !important; }
            .bar-color { fill: #9f9178 !important; }
        }
    '''

    card = ET.SubElement(svg, 'g', {'class': 'card'})
    ET.SubElement(card, 'rect', {
        'class': 'card-bg',
        'x': '0',
        'y': '0',
        'width': str(svg_width),
        'height': str(svg_height),
        'rx': str(card_radius)
    })

    title = ET.SubElement(svg, 'text', {
        'x': str(padding + 25),
        'y': str(padding - 5),
        'class': 'text language',
        'style': 'font-size: 18px; font-weight: 600;'
    })
    title.text = 'Most Used Languages:'

    sorted_languages = sorted(
        language_percentages.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
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
            'class': 'bar bar-color',
            'x': str(padding + 25),
            'y': str(text_offset),
            'width': str((percentage / 100) * max_bar_width),
            'height': str(bar_height),
            'rx': '4',
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
        print("\nGenerating SVG...")
        create_language_svg(language_percentages)
        print("Generated SVG as 'stats.svg'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
