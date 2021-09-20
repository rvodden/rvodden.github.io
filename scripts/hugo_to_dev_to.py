from typing import Dict
import click, re, yaml
from ruamel.yaml import YAML
from io import StringIO

def displaymatch(match):
    if match is None:
        return None
    return '<Match: %r, groups=%r>' % (match.group(), match.groups())

START_COMMENT = r"{{% skip %}}"
END_COMMENT = r"{{% /skip %}}"

START_LATEX_INLINE = r"{% katex inline %}"
END_LATEX_INLINE = r"{% endkatex %}"

def remove_comments(contents: str) -> str:
    REMOVE_COMMENTS_PATTERN = re.compile(f"{START_COMMENT}.*?{END_COMMENT}", flags=re.MULTILINE | re.DOTALL)
    return re.sub(REMOVE_COMMENTS_PATTERN, "", contents)

def replace_latex_delimeters(contents: str) -> str:
    SWAP_OUT_LATEX_PATTERN = re.compile(r"[$](.*?)[$]", flags=re.MULTILINE | re.DOTALL)
    return re.sub(SWAP_OUT_LATEX_PATTERN, f"{START_LATEX_INLINE}\\1{END_LATEX_INLINE}", contents)
    
def split_preamble_and_content(content: str) -> str:
    PREAMBLE_DELIMETER = '---'
    pattern = re.compile(f"{PREAMBLE_DELIMETER}(.*?){PREAMBLE_DELIMETER}(.*)", flags=re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    return {
        'preamble': yaml.safe_load(match.group(1)),
        'content': match.group(2)
    }

def convert_content(contents: str) -> str:
    contents = remove_comments(contents)
    contents = replace_latex_delimeters(contents)
    return contents

def canonical_url(filename: str) -> str:
    filename = filename.split('/')[-1]
    return "https://vodden.com/posts/" + filename[11:-3] + '/'

def convert_preamble(preamable: Dict[str, str], filename: str) -> Dict[str, str]:
    retval = {}
    copy_through = ['title', 'description']
    convert = {
        'categories': 'tags'
    }
    
    for key in copy_through:
        try: 
            retval[key] = preamable[key]
        except KeyError: #Missing keys are not an issue
            continue

    for key, value in convert.items():
        try:
            retval[value] = preamable[key]
        except KeyError: #Missing keys are not an issue
            continue

    
    retval['published'] = not preamable['draft']
    if 'series' in preamable.keys():
        retval['series'] = preamable['series'][0]
    retval['canonical_url'] = canonical_url(filename)
    return retval

def convert_to_body_markdown(article: Dict[str, str]) -> str:
    # TODO: this is duplicated in the DevToClient
    stream = StringIO()
    yaml = YAML()
    yaml.dump(article['preamble'], stream)
    preamble = stream.getvalue()
    return f"---\n{preamble}---\n{article['content']}\n"

def convert_hugo_article_to_dev_to(article: str) -> Dict[str,str]:
    retval = {}
    
    retval['preamble'] = convert_preamble(article['preamble'], article['filename'])
    retval['content'] = convert_content(article['content'])

    return retval

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def main(filename):
    with open(filename) as file:
        text = file.read()
    article = split_preamble_and_content(text)
    article['filename']=filename
    dev_to_article = convert_hugo_article_to_dev_to(article)
    dev_to_article = convert_to_body_markdown(dev_to_article)
    print(dev_to_article)

if __name__ == '__main__':
    main()